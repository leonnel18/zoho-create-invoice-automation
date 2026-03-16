# SOP-05: File Rename
**Tool:** `tools/rename_source.py`

## Goal
Rename processed delivery receipt PDFs to mark them as done.

## Rename Pattern
`{original_name}_Invoice Generated_{YYYY-MM-DD}.pdf`
Date used: today's processing date (not invoice date).

## Trigger Condition
Only called AFTER zoho_invoice_id is confirmed in DB. Never rename on error.

## Idempotency
Orchestrator skips any file whose name already contains `_Invoice Generated_`.
