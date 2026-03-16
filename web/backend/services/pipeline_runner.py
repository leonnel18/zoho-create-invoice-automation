"""
Run the existing pipeline tools as a subprocess with per-user credentials
injected via environment variables. Zero changes to tools/ scripts required.
"""
import asyncio
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

from ..config import TOOLS_DIR
from ..core.crypto import decrypt
from ..database import SessionLocal
from ..models import InvoiceJob, UserSettings

# Module-level registry of running subprocesses keyed by job_id.
# Allows cancel_job() to kill a process from the stop endpoint.
_running: dict[int, subprocess.Popen] = {}  # type: ignore[type-arg]

TIMEOUT_SECONDS = 300  # 5 minutes


def cancel_job(job_id: int) -> bool:
    """Kill the subprocess for job_id if it is still running. Returns True if killed."""
    proc = _running.get(job_id)
    if proc and proc.poll() is None:
        proc.kill()
        return True
    return False


async def run_pipeline_for_user(
    user_id: int,
    db,
    triggered_by: str = "manual",
) -> int:
    """
    Creates an InvoiceJob row, spawns orchestrator.py as a subprocess with
    the user's credentials in env, captures stdout into job.log_output,
    then marks the job done.

    Returns the job ID (int).
    """
    s: UserSettings | None = (
        db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    )
    if not s:
        raise ValueError("UserSettings not found")

    # Create job record (running)
    job = InvoiceJob(
        user_id=user_id,
        triggered_by=triggered_by,
        status="running",
        started_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id: int = job.id

    # Build per-user environment
    env = {
        **os.environ,
        "INPUT_FOLDER":       s.input_folder or "",
        "OUTPUT_FOLDER":      s.output_folder or "",
        "DB_PATH":            s.db_path or "",
        "ZOHO_CLIENT_ID":     s.zoho_client_id or "",
        "ZOHO_CLIENT_SECRET": decrypt(s.zoho_client_secret) if s.zoho_client_secret else "",
        "ZOHO_REFRESH_TOKEN": decrypt(s.zoho_refresh_token) if s.zoho_refresh_token else "",
        "ZOHO_ORG_ID":        s.zoho_org_id or "",
        "ZOHO_REGION":        s.zoho_region or "com",
        "DEFAULT_ITEM_RATE":  str(s.default_item_rate or 1.0),
        "DEFAULT_CUSTOMER":   s.default_customer or "Generic",
    }

    orchestrator = str(TOOLS_DIR / "orchestrator.py")

    # Schedule background task — do NOT pass the request-scoped db (closes after response)
    asyncio.create_task(
        _run_and_update(job_id, orchestrator, env)
    )

    return job_id


async def _run_and_update(
    job_id: int,
    orchestrator: str,
    env: dict,
) -> None:
    """
    Async task: runs orchestrator.py via subprocess.Popen inside a thread-pool
    executor (avoids Windows SelectorEventLoop incompatibility with
    asyncio.create_subprocess_exec), then updates the job row using a fresh
    DB session.
    """
    log_lines: list[str] = []
    exit_code = -1

    try:
        loop = asyncio.get_event_loop()

        def _run() -> tuple[list[str], int]:
            proc = subprocess.Popen(
                [sys.executable, orchestrator],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                errors="replace",
            )
            _running[job_id] = proc
            try:
                stdout, _ = proc.communicate(timeout=TIMEOUT_SECONDS)
                lines = [ln.rstrip() for ln in stdout.splitlines()]
                rc = proc.returncode if proc.returncode is not None else -1
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, _ = proc.communicate()
                lines = [ln.rstrip() for ln in stdout.splitlines()]
                lines.append(f"[timeout] Job stopped automatically after {TIMEOUT_SECONDS // 60} minutes")
                rc = -2
            finally:
                _running.pop(job_id, None)
            return lines, rc

        result: tuple[list[str], int] = await loop.run_in_executor(None, _run)  # type: ignore[arg-type]
        log_lines, exit_code = result

    except Exception as exc:
        log_lines.append(f"[runner error] {type(exc).__name__}: {exc}")
        exit_code = -1
        _running.pop(job_id, None)

    # Use a fresh session — the request-scoped session is already closed
    db = SessionLocal()
    try:
        job = db.get(InvoiceJob, job_id)
        if job:
            job.status = "done" if exit_code == 0 else "error"
            job.log_output = "\n".join(log_lines)
            job.finished_at = datetime.now(timezone.utc).isoformat()
            # Parse counts from the orchestrator summary line:
            # "Done. Invoices pushed: 4 | Errors: 0"
            full_log = job.log_output
            m_pushed = re.search(r"Invoices pushed:\s*(\d+)", full_log)
            m_errors = re.search(r"Errors:\s*(\d+)", full_log)
            job.invoices_pushed = int(m_pushed.group(1)) if m_pushed else 0
            job.errors = int(m_errors.group(1)) if m_errors else 0
            db.commit()
    finally:
        db.close()
