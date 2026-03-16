# task_plan.md — Project Blueprint
## zoho-create-invoice-automation | [Dev-Hobby]

---

## Phases & Checklist

### 🟡 Phase 0: Protocol Initialization
- [x] Create project directory
- [x] Initialize `claude.md`, `task_plan.md`, `findings.md`, `progress.md`
- [x] Answer all 5 Discovery Questions
- [x] Confirm Data Schema in `claude.md`
- [ ] **HALT — Blueprint approval required before Phase 2**

---

### ✅ Phase 1: Blueprint (Vision & Logic)
- [x] Discovery Questions answered
- [x] DB platform confirmed → SQLite
- [x] Folder paths confirmed → configurable via `.env`
- [x] PDF template structure confirmed → Date, Qty, Unit, Item Name, Group, Total(blank→rate=1.00)
- [x] Cron schedule confirmed → 6PM daily + `run_pipeline.bat`
- [x] Zoho Books credentials confirmed → MCP URL + API Key
- [x] Data Schema finalized in `claude.md`
- [x] Blueprint approved by Gino

---

### ✅ Phase 2: Link (Connectivity)
- [x] Directory structure created (`architecture/`, `tools/`, `.tmp/`)
- [x] `.env.example` and `requirements.txt` created
- [x] `tools/verify_zoho.py` built — Zoho REST API verified
- [x] `tools/verify_sqlite.py` built — DB init + schema creation
- [x] `.env` populated — Zoho Books REST API connected
- [x] Zoho region confirmed: `com`
- [x] Org confirmed: Greenhouse Fruit & Vegetable Inc. (884719445)
- [x] Items endpoint returning data ✅

---

### ✅ Phase 3: Architect (3-Layer Build)

**Layer 1 — Architecture SOPs**
- [ ] `architecture/01_pdf_parser.md`
- [ ] `architecture/02_db_store.md`
- [ ] `architecture/03_zoho_push.md`
- [ ] `architecture/04_invoice_pdf_generate.md`
- [ ] `architecture/05_file_rename.md`
- [ ] `architecture/06_cron_orchestrator.md`

**Layer 3 — Tools**
- [ ] `tools/parse_pdf.py` — extract fields from delivery receipt PDFs
- [ ] `tools/db_store.py` — save parsed records to DB
- [ ] `tools/zoho_push.py` — create/verify items + push invoice to Zoho Books
- [ ] `tools/generate_pdf.py` — download/generate invoice PDF from Zoho
- [ ] `tools/rename_source.py` — rename processed source files
- [ ] `tools/orchestrator.py` — main pipeline runner (called by cron)

---

### ⬜ Phase 4: Stylize
- [ ] Invoice PDF format reviewed
- [ ] DB schema/UI review (if applicable)
- [ ] Error log output format finalized

---

### ⬜ Phase 5: Trigger (Deployment)
- [ ] Cron job configured
- [ ] End-to-end test on real receipt
- [ ] Maintenance log updated in `claude.md`

---

## Open Questions (Pre-Blueprint)

1. DB platform: SQLite (local) vs Notion vs other?
2. What are the exact input/output folder paths?
3. Can you share or describe the PDF template structure?
4. Cron schedule — how often should this run?
5. Zoho Books Org ID confirmed?
