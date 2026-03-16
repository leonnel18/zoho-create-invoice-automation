# progress.md — Run Log
## zoho-create-invoice-automation | [Dev-Hobby]

---

## 2026-03-16

### Session 1
- **Status:** Phase 2 complete. Zoho Books REST API verified. Moving to Phase 3.
- **Done:**
  - Protocol 0: project initialized, all planning docs created
  - Phase 1: Blueprint approved — SQLite DB, rate=1.00, Generic customer, .bat + cron trigger
  - Phase 2: Zoho MCP abandoned (not designed for direct HTTP) → switched to Zoho Books REST API
  - OAuth2 refresh token flow confirmed working on `.com` region
  - Org verified: Greenhouse Fruit & Vegetable Inc. (org_id: 884719445)
  - SQLite verify script ready
- **Errors resolved:**
  - Zoho MCP `INVALID_URL_PATTERN` → wrong endpoint (needed `/mcp/message?key=`)
  - MCP auth `401` → MCP not designed for direct calls, switched to REST API
  - Token `invalid_code` → refresh token was a grant code, regenerated properly
  - Books `401 code:57` → missing ZohoBooks scopes on grant, regenerated with correct scopes
- **Next:** Phase 4 — installer wizard (tkinter, Windows + Mac) + Task Scheduler setup

### Session 2
- **Status:** Phase 3 complete. End-to-end pipeline verified.
- **Done:**
  - Built all 6 tools: `parse_pdf`, `db_store`, `zoho_client`, `zoho_push`, `generate_pdf`, `rename_source`, `orchestrator`
  - Built all 6 Architecture SOPs
  - PDF parsing handles multi-customer files (1 PDF → N invoices by Company Name)
  - Company Name extracted from page header; fallback to "Generic"
  - Zoho token caching fixed (was causing rapid-fire refresh → token invalidation)
  - due_date = posting date + 15 days
  - End-to-end test: 4 invoices pushed, 4 PDFs generated, 2 source files renamed
  - Idempotency confirmed: re-run returns "No new PDFs to process"
- **Errors resolved:**
  - `401 code:57` (all calls) → scope insufficient → regenerated token with `ZohoBooks.fullaccess.all`
  - `400 txn_posting_date missing` → added to invoice payload
  - Rapid-fire token refresh → implemented in-memory token caching in `zoho_client.py`
- **Next:** Phase 4 — installer wizard + Phase 5 — Task Scheduler / cron deployment

