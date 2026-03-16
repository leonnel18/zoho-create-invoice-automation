# SOP-02: DB Store
**Tool:** `tools/db_store.py`

## Goal
SQLite CRUD for pipeline state. Single source of truth for all invoice processing status.

## Schema
```sql
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
```

## Operations
- `record_exists(source_file)` → bool — idempotency check before insert
- `insert_invoice(parsed)` → id — INSERT OR IGNORE (safe to re-run)
- `update_pushed(source_file, zoho_invoice_id)` → sets status='pushed', processed_at=now
- `update_pdf_path(source_file, pdf_output_path)` → stores output PDF path
- `update_error(source_file, error_message)` → sets status='error'
- `get_pending()` → list of pending records for retry/reprocessing

## Invariants
- `source_file` is UNIQUE — prevents duplicate invoice creation
- Re-running on a 'pushed' record is a no-op (orchestrator checks status before processing)
