import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
import aiofiles
from ..database import get_db
from ..models import User, UserSettings, InvoiceJob
from ..schemas.job import JobRead, JobStarted
from ..core.dependencies import get_current_user
from ..services.pipeline_runner import run_pipeline_for_user, cancel_job

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run", response_model=JobStarted, status_code=202)
async def run_pipeline(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s or not s.input_folder:
        raise HTTPException(400, "Folder settings not configured")
    if not s.zoho_client_id:
        raise HTTPException(400, "Zoho credentials not configured")

    job_id = await run_pipeline_for_user(user.id, db, triggered_by="manual")
    return JobStarted(job_id=job_id)


@router.get("/status/{job_id}", response_model=JobRead)
def job_status(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(InvoiceJob).filter(
        InvoiceJob.id == job_id,
        InvoiceJob.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.post("/stop/{job_id}")
def stop_pipeline(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(InvoiceJob).filter(
        InvoiceJob.id == job_id,
        InvoiceJob.user_id == user.id,
    ).first()
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status != "running":
        raise HTTPException(400, "Job is not running")
    killed = cancel_job(job_id)
    if not killed:
        # Process already finished; just mark it
        job.status = "error"
        job.log_output = (job.log_output or "") + "\n[stopped by user]"
        job.finished_at = datetime.now(timezone.utc).isoformat()
        db.commit()
    return {"ok": True, "killed": killed}


@router.post("/upload", response_model=JobStarted, status_code=202)
async def upload_and_run(
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept uploaded PDFs, save to /tmp, and trigger the pipeline."""
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s or not s.zoho_client_id:
        raise HTTPException(400, "Zoho credentials not configured")
    if not files:
        raise HTTPException(400, "No files provided")

    # Validate all files are PDFs before saving any
    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            raise HTTPException(400, f"Only PDF files are accepted: {f.filename}")

    # Save uploaded PDFs to a per-user temp dir
    tmp_dir = f"/tmp/pipeline/{user.id}"
    input_dir = f"{tmp_dir}/input"
    output_dir = f"{tmp_dir}/output"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for f in files:
        content = await f.read()
        dest = os.path.join(input_dir, os.path.basename(f.filename))  # type: ignore[arg-type]
        async with aiofiles.open(dest, "wb") as fp:
            await fp.write(content)

    job_id = await run_pipeline_for_user(
        user.id, db,
        triggered_by="upload",
        env_overrides={
            "INPUT_FOLDER":  input_dir,
            "OUTPUT_FOLDER": output_dir,
            "DB_PATH":       f"{tmp_dir}/invoices.db",
            "DEDUP_ENABLED": "false" if (s and s.dedup_enabled is False) else "true",
        },
    )
    return JobStarted(job_id=job_id)


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(InvoiceJob)
        .filter(InvoiceJob.user_id == user.id)
        .order_by(InvoiceJob.id.desc())
        .limit(limit)
        .all()
    )
