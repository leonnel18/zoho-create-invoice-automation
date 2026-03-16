# SOP-01: PDF Parser
**Tool:** `tools/parse_pdf.py`

## Goal
Extract structured invoice data from a templated delivery receipt PDF.

## Input
- PDF file path

## Output
Returns a **list** of invoice dicts — one per unique customer found in the file.
```json
[
  {
    "date":          "YYYY-MM-DD",
    "customer_name": "JIN CAI UNLIMITED CORP",
    "items": [
      { "item_name": "string", "item_group": "string", "qty": 1.0, "unit": "string", "total": null }
    ],
    "source_file":  "pdf_basename::CustomerName",
    "pdf_source":   "/path/to/original.pdf"
  }
]
```

## PDF Structure
- **Header** (above table): `Company Name: <value>` — extracted via regex from full page text
- **Table columns** (in order): Date | Qty | Unit | Item Name | Item Level Group Name | Total
- **Footer**: Driver Name, Plate No, Assistant — ignored

### Customer Name Extraction
- Regex: `Company Name:\s*(.+?)(?:\n|$)` on full page text
- If matched and non-empty → use extracted value as `customer_name`
- If blank or not found → use `DEFAULT_CUSTOMER_NAME` env var (default: `"Generic"`)

### Multi-Customer PDF Handling
- One PDF file can contain multiple pages, each for a different customer
- Items are grouped by `(customer_name, date)` across all pages
- Pages with no table rows (e.g., overflow footer pages) are skipped
- Result: one invoice dict per unique `(customer_name, date)` combination

## Edge Cases
- **Qty line-wrap**: Large values (e.g., 85.00) may render as "85.0\n0" — join and parse as float
- **None/empty cells**: Treat as empty string, skip row if item_name is blank
- **Multi-page PDFs**: Process all pages, merge items into one list
- **Header row detection**: Skip rows where first cell matches "Date" or similar header text

## Error Handling
- If date cannot be parsed: skip row, log warning
- If qty cannot be parsed: default to 0.0, log warning
- If no items extracted: raise ValueError — do not insert empty invoices into DB
