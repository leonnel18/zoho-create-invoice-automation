import os
import sqlite3
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserSettings
from ..core.dependencies import get_current_user
from ..config import CLOUD_MODE

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

PDF_TTL_SECONDS = 4 * 3600  # 4 hours


def _cloud_db_path(user_id: int) -> str:
    return f"/tmp/pipeline/{user_id}/invoices.db"


def _resolve_db_path(user_id: int, settings_db_path: str | None) -> str | None:
    if CLOUD_MODE:
        return _cloud_db_path(user_id)
    return settings_db_path


def _read_user_invoices(db_path: str, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
    """Read from the user's own pipeline invoices.db. Returns (rows, total_count)."""
    try:
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        total = con.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        rows = con.execute(
            "SELECT * FROM invoices ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows], total
    except Exception:
        return [], 0


def _invoice_stats(db_path: str) -> dict:
    try:
        con = sqlite3.connect(db_path)
        cur = con.execute(
            "SELECT status, COUNT(*) AS cnt FROM invoices GROUP BY status"
        )
        stats = {row[0]: row[1] for row in cur.fetchall()}
        con.close()
        pending = stats.get("pending", 0)
        pushed  = stats.get("pushed",  0)
        error   = stats.get("error",   0)
        return {"pending": pending, "pushed": pushed, "error": error,
                "total": pending + pushed + error}
    except Exception:
        return {"pending": 0, "pushed": 0, "error": 0, "total": 0}


@router.get("")
def list_invoices(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    db_path = _resolve_db_path(user.id, s.db_path if s else None)
    if not db_path:
        return {"items": [], "total": 0, "page": page}
    offset = (page - 1) * page_size
    items, total = _read_user_invoices(db_path, page_size, offset)
    return {"items": items, "total": total, "page": page}


@router.get("/stats")
def invoice_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    db_path = _resolve_db_path(user.id, s.db_path if s else None)
    if not db_path:
        return {"pending": 0, "pushed": 0, "error": 0, "total": 0}
    return _invoice_stats(db_path)


@router.get("/{record_id}/pdf")
def download_invoice_pdf(
    record_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    db_path = _resolve_db_path(user.id, s.db_path if s else None)
    if not db_path:
        raise HTTPException(status_code=404, detail="No invoice database found")

    try:
        con = sqlite3.connect(db_path)
        row = con.execute(
            "SELECT pdf_output_path FROM invoices WHERE id = ?", (record_id,)
        ).fetchone()
        con.close()
    except Exception:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="No PDF generated for this invoice")

    pdf_path = row[0]
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="PDF expired or not available")

    age = time.time() - os.path.getmtime(pdf_path)
    if age > PDF_TTL_SECONDS:
        raise HTTPException(status_code=404, detail="PDF expired (older than 4 hours)")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )
