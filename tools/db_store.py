"""
db_store.py
Layer 3 Tool — SQLite CRUD for the invoices pipeline.
Single source of truth for processing state.
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "invoices.db")


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def record_exists(source_file: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            "SELECT id FROM invoices WHERE source_file = ?", (source_file,)
        ).fetchone()
    return row is not None


def get_status(source_file: str) -> str | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT status FROM invoices WHERE source_file = ?", (source_file,)
        ).fetchone()
    return row[0] if row else None


def insert_invoice(parsed: dict) -> int:
    """Insert a new pending invoice record. Safe to re-run (INSERT OR IGNORE)."""
    with _conn() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO invoices
                (source_file, invoice_date, customer_name, items_json, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (
                parsed["source_file"],
                parsed["date"],
                parsed["customer_name"],
                json.dumps(parsed["items"]),
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0


def update_pushed(source_file: str, zoho_invoice_id: str):
    with _conn() as conn:
        conn.execute(
            """
            UPDATE invoices
            SET zoho_invoice_id = ?, status = 'pushed', processed_at = ?
            WHERE source_file = ?
            """,
            (zoho_invoice_id, datetime.now().isoformat(), source_file),
        )
        conn.commit()


def update_pdf_path(source_file: str, pdf_output_path: str):
    with _conn() as conn:
        conn.execute(
            "UPDATE invoices SET pdf_output_path = ? WHERE source_file = ?",
            (pdf_output_path, source_file),
        )
        conn.commit()


def update_error(source_file: str, error_message: str):
    with _conn() as conn:
        conn.execute(
            "UPDATE invoices SET status = 'error', error_message = ? WHERE source_file = ?",
            (error_message, source_file),
        )
        conn.commit()


def get_pending() -> list:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT source_file, invoice_date, customer_name, items_json "
            "FROM invoices WHERE status = 'pending'"
        ).fetchall()
    return [
        {
            "source_file":   r[0],
            "date":          r[1],
            "customer_name": r[2],
            "items":         json.loads(r[3]),
        }
        for r in rows
    ]
