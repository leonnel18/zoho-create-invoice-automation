# SOP-06: Orchestrator
**Tool:** `tools/orchestrator.py`
**Trigger:** `run_pipeline.bat` (manual) or Windows Task Scheduler (daily 6PM)

## Goal
Coordinate all tools in order. Process all unhandled PDFs in INPUT_FOLDER end-to-end.

## Flow Per File
```
scan INPUT_FOLDER
  → skip if filename contains "_Invoice Generated_"
  → skip if DB record exists with status='pushed'
  → parse_pdf()         → structured dict
  → insert_invoice()    → DB record (status: pending)
  → push_invoice()      → zoho_invoice_id
  → update_pushed()     → DB status: pushed
  → download_pdf()      → saved to OUTPUT_FOLDER
  → update_pdf_path()   → DB updated
  → rename_source()     → file renamed
```

## Error Handling
- Any step fails: log error to DB (status='error'), continue to next file
- Print summary at end: N processed, N errors

## Idempotency
- Files with `_Invoice Generated_` in name: skipped
- DB records with status='pushed': skipped
- Safe to re-run at any time
