"""
verify_sqlite.py
Phase 2: Link — Initialize SQLite DB and confirm schema creation.
Safe to re-run (CREATE TABLE IF NOT EXISTS).
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "invoices.db")


def init_db() -> bool:
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) if os.path.dirname(DB_PATH) else None
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file     TEXT NOT NULL UNIQUE,
                invoice_date    TEXT NOT NULL,
                customer_name   TEXT NOT NULL DEFAULT 'Generic',
                items_json      TEXT NOT NULL,
                zoho_invoice_id TEXT DEFAULT NULL,
                pdf_output_path TEXT DEFAULT NULL,
                status          TEXT CHECK(status IN ('pending','pushed','error')) DEFAULT 'pending',
                error_message   TEXT DEFAULT NULL,
                processed_at    TEXT DEFAULT NULL
            )
        """)
        conn.commit()
        conn.close()
        print(f"[OK] SQLite DB ready at: {DB_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] SQLite init failed: {e}")
        return False


if __name__ == "__main__":
    ok = init_db()
    exit(0 if ok else 1)
