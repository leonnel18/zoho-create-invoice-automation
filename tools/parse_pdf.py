"""
parse_pdf.py
Layer 3 Tool — Extract structured invoice data from delivery receipt PDFs.

PDF structure (per page):
  - Header: "Company Name: <value>" (above the table)
  - Table columns: Date | Qty | Unit | Item Name | Item Level Group Name | Total
  - Footer: Driver Name, Plate No, Assistant (ignored)

One PDF may contain multiple pages, each for a different customer.
Returns: list of invoice dicts (one per unique customer found in the file).

Usage:
    python tools/parse_pdf.py path/to/receipt.pdf
"""

import os
import re
import sys
import json
import pdfplumber
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CUSTOMER = os.getenv("DEFAULT_CUSTOMER_NAME", "Generic")
HEADER_KEYWORDS  = {"date", "qty", "unit", "item name", "item level group name", "total"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_date(raw: str) -> str:
    """Convert MM/DD/YYYY → YYYY-MM-DD."""
    raw = raw.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unparseable date: {raw}")


def clean_qty(raw: str) -> float:
    """
    Handle qty values with PDF line-wrap.
    e.g. '85.0\\n0' → join parts → '85.00' → 85.0
    """
    raw   = raw.strip()
    parts = [p.strip() for p in raw.split("\n") if p.strip()]
    if not parts:
        return 0.0
    if len(parts) == 2:
        try:
            return float(parts[0] + parts[1])
        except ValueError:
            pass
    try:
        return float(parts[0])
    except ValueError:
        return 0.0


def extract_company_name(page_text: str) -> str | None:
    """Extract 'Company Name: <value>' from page header text."""
    match = re.search(r"Company\s+Name\s*[:\-]\s*(.+?)(?:\n|$)", page_text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        return name if name else None
    return None


def is_header_row(row: list) -> bool:
    values = {str(v or "").lower().strip() for v in row}
    return bool(values & HEADER_KEYWORDS)


def is_data_row(row: list) -> bool:
    if not row or not row[0]:
        return False
    return bool(re.match(r"\d{2}/\d{2}/\d{4}", str(row[0]).strip()))


# ── Main parser ───────────────────────────────────────────────────────────────

def parse_pdf(pdf_path: str) -> list:
    """
    Parse a delivery receipt PDF.
    Returns a list of invoice dicts — one per unique customer found in the file.
    Each invoice dict:
        {
            "date":          "YYYY-MM-DD",
            "customer_name": "string",
            "items":         [...],
            "source_file":   "pdf_basename::customer_name"  ← unique DB key
        }
    """
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]

    # bucket: key = (customer_name, date) → list of items
    buckets = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text    = page.extract_text() or ""
            company_name = extract_company_name(page_text) or DEFAULT_CUSTOMER

            table = page.extract_table()
            if not table:
                continue

            for row in table:
                if is_header_row(row) or not is_data_row(row):
                    continue

                row = (list(row) + [None] * 6)[:6]
                date_raw, qty_raw, unit, item_name, item_group, _total = row

                try:
                    date_str = parse_date(str(date_raw))
                except ValueError:
                    continue

                item_name_clean = str(item_name or "").strip()
                if not item_name_clean:
                    continue

                qty = clean_qty(str(qty_raw or "0"))

                key = (company_name, date_str)
                if key not in buckets:
                    buckets[key] = []

                buckets[key].append({
                    "item_name":  item_name_clean,
                    "item_group": str(item_group or "").strip(),
                    "qty":        qty,
                    "unit":       str(unit or "").strip(),
                    "total":      None,
                })

    if not buckets:
        raise ValueError(f"No items extracted from: {pdf_path}")

    invoices = []
    for (customer_name, date_str), items in buckets.items():
        # Sanitize customer name for use as part of DB key
        safe_name   = re.sub(r"[^a-zA-Z0-9 _\-]", "", customer_name).strip()
        source_file = f"{pdf_basename}::{safe_name}"

        invoices.append({
            "date":          date_str,
            "customer_name": customer_name,
            "items":         items,
            "source_file":   source_file,
            "pdf_source":    pdf_path,   # original file path (for rename step)
        })

    return invoices


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/parse_pdf.py <path_to_pdf>")
        sys.exit(1)
    results = parse_pdf(sys.argv[1])
    print(f"Found {len(results)} invoice(s):\n")
    for inv in results:
        print(f"  Customer : {inv['customer_name']}")
        print(f"  Date     : {inv['date']}")
        print(f"  Items    : {len(inv['items'])}")
        print(f"  Key      : {inv['source_file']}")
        print()
    print(json.dumps(results, indent=2))
