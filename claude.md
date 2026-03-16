# claude.md — Project Constitution
## zoho-create-invoice-automation | [Dev-Hobby]

> **Law file.** Only update when: schema changes, rule added, or architecture modified.

---

## Project Identity

| Field | Value |
|-------|-------|
| Mental Folder | [Dev-Hobby] |
| Owner | Gino |
| Status | 🟡 Blueprint Phase |
| Started | 2026-03-16 |

---

## North Star

Parse templated delivery receipt PDFs → extract structured data → store in DB → push to Zoho Books as invoices → generate invoice PDFs → rename processed source files.

---

## Data Schema (v1 — Pending Total Column Confirmation)

### Config Variables (stored in `.env`)
```
INPUT_FOLDER=C:/path/to/delivery-receipts/
OUTPUT_FOLDER=C:/path/to/generated-invoices/
DB_PATH=C:/path/to/invoices.db
ZOHO_MCP_BASE_URL=https://...
ZOHO_API_KEY=...
DEFAULT_ITEM_RATE=1.00
```

### Input: Delivery Receipt PDF
Columns: Date | Qty | Unit | Item Name | Item Level Group Name | Total
Header (above table): `Company Name: <value>`

`parse_pdf()` returns a **list** (one PDF can contain multiple customers):
```json
[
  {
    "date":          "YYYY-MM-DD",
    "customer_name": "string (from 'Company Name:' header; fallback: DEFAULT_CUSTOMER_NAME)",
    "items": [
      {
        "item_name":  "string",
        "item_group": "string",
        "qty":        "float",
        "unit":       "string",
        "total":      null
      }
    ],
    "source_file": "pdf_basename::CustomerName  ← unique DB key per customer per file",
    "pdf_source":  "string (original file path, used for rename step)"
  }
]
```

### DB Record (SQLite — Intermediate Store)
```json
{
  "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
  "source_file": "TEXT",
  "invoice_date": "TEXT (YYYY-MM-DD)",
  "customer_name": "TEXT DEFAULT 'Generic'",
  "items_json": "TEXT (JSON blob of items array)",
  "zoho_invoice_id": "TEXT DEFAULT NULL",
  "pdf_output_path": "TEXT DEFAULT NULL",
  "status": "TEXT CHECK(status IN ('pending','pushed','error')) DEFAULT 'pending'",
  "error_message": "TEXT DEFAULT NULL",
  "processed_at": "TEXT DEFAULT NULL"
}
```

### Output: Zoho Books Invoice Payload
```json
{
  "customer_name": "string",
  "date": "YYYY-MM-DD",
  "line_items": [
    {
      "item_id": "string (Zoho item ID — looked up or created)",
      "name": "string",
      "quantity": "float",
      "unit": "string",
      "rate": "float → hardcoded 1.00 (constant, update via config later)"
    }
  ]
}
```

---

## Behavioral Rules

1. `customer_name` is extracted from `Company Name:` header on each PDF page → fallback to `"Generic"` if blank or absent
2. If item does not exist in Zoho Books → create item first (`POST /items`), then reference in invoice
3. Processed source files are renamed: `{original_name}_Invoice Generated_{YYYY-MM-DD}.pdf`
4. Generated invoice PDFs saved to `OUTPUT_FOLDER` (from `.env`)
5. All intermediate files go to `.tmp/`
6. DB (`invoices` table in SQLite) is the single source of truth for pipeline state
7. Pipeline is idempotent: files already renamed (containing `_Invoice Generated_`) are skipped
8. Cron: daily at 6:00 PM via Windows Task Scheduler + manual trigger via `run_pipeline.bat`
9. Folder paths and credentials are never hardcoded — always read from `.env`
10. Line item `rate` is always `1.00` (constant) — updateable via `.env` key `DEFAULT_ITEM_RATE`

---

## Architecture Invariants

- LLM does routing only — no deterministic business logic embedded in prompts
- Each `tools/` script is atomic and independently testable
- `.env` holds all credentials — never hardcoded
- Pipeline is idempotent: re-running on already-processed files must be a no-op

---

## Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| 2026-03-16 | Initial constitution created | Gino + Claude |
| 2026-03-16 | Phase 3 complete — pipeline verified end-to-end. 4 invoices pushed. | Gino + Claude |
| 2026-03-16 | Added: multi-customer PDF parsing, Company Name extraction, token caching, due_date +15d | Gino + Claude |

