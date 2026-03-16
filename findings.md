# findings.md — Research & Discoveries
## zoho-create-invoice-automation | [Dev-Hobby]

---

## 2026-03-16 — Initial Research

### PDF Parsing Libraries (Python)
| Library | Strengths | Weaknesses |
|---------|-----------|------------|
| `pdfplumber` | Best for structured/tabular PDFs, precise bounding box extraction | Slower on large batches |
| `PyMuPDF (fitz)` | Fast, accurate text extraction, can render pages | Slightly more complex API |
| `pypdf2` / `pypdf` | Simple, widely used | Poor table handling |
| **Recommendation** | **`pdfplumber`** for templated receipts with tables | — |

### Database Options
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **SQLite** | Zero-config, local, Python native (`sqlite3`), no server | No web UI out of the box | ✅ Best for Dev-Hobby |
| Notion | Good visibility, API available | Rate limits, not ACID, overkill for structured data pipeline | ⚠️ Acceptable if Gino wants human-readable log |
| Airtable | Good UI | External dependency, free tier limits | ❌ Overkill |
| PostgreSQL | Full-featured | Requires server setup | ❌ Overkill |
| **SQLite + DB Browser** | SQLite with free GUI (DB Browser for SQLite) | — | ✅ Recommended |

**Recommendation:** SQLite with [DB Browser for SQLite](https://sqlitebrowser.org/) for visibility. Lightweight, no server, Python native, and fully queryable. If Gino wants cloud visibility, Notion can be used as a *notification layer* (log row added on each invoice push) on top of SQLite as the primary store.

### Zoho Books Invoice API
- Endpoint: `POST /invoices` (Zoho Books API v3)
- Requires: `customer_id`, `line_items[].item_id`, `date`
- Item creation: `POST /items` if item not found by name
- PDF generation: `GET /invoices/{invoice_id}?accept=pdf`
- Auth: OAuth2 (access token + refresh token) or API Key via MCP

### Cron/Task Scheduler
- Windows: Task Scheduler (native) or Python `schedule` library
- Recommendation: Task Scheduler calling `python orchestrator.py` on defined interval

---

## 2026-03-16 — PDF Template Analysis (Sample Delivery Receipt)

### Confirmed Column Structure
| Column | Type | Notes |
|--------|------|-------|
| Date | MM/DD/YYYY per row | All rows share same date — use first row's date as invoice date |
| Qty | float | Can be decimal (e.g., 0.50, 85.00). **Parsing risk:** large Qty values may wrap to next line in PDF (e.g., "85.00" renders as "85.0\n0") — need line-merge logic |
| Unit | string | e.g., PC, PACK, KG |
| Item Name | string | Can contain special chars, hyphens, parentheses |
| Item Level Group Name | string | e.g., Highland, Leafy, Lowland, Rootcrops, Imported Fruits |
| Total | float or BLANK | **⚠️ CRITICAL: Total column is blank in sample.** See open question below. |

### No Customer Name Field
- Delivery receipt has no customer/consignee field → confirm "Generic" as default (already in rules)

### Footer Fields (Driver Name, Plate No, Assistant)
- Not needed for Zoho invoice — skip during parsing

### PDF Parsing Risks
1. **Qty line-wrap**: Large quantities (e.g., 85.00) may split across lines → need post-extraction merge
2. **Item Name formatting**: Some names have special chars — strip safely, don't truncate
3. **Multi-page receipts**: Unknown — must handle gracefully

### ⚠️ Open Question: Total Column Blank
The Total column in the sample is completely empty. Two possibilities:
- **A**: Total is always blank — receipt is quantity-only, no pricing. Zoho item rates must come from the **Zoho Books item master**.
- **B**: Sample was unfilled — real receipts have totals per row.
**This must be confirmed before Schema is finalized.**

---

## Constraints
- Zoho Books item names must be unique — lookup before create
- PDF rename must only happen after confirmed `zoho_invoice_id` is stored in DB
- Pipeline must be idempotent — files already processed (renamed) must be skipped

