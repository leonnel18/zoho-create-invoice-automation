"""
generate_pdf.py
Layer 3 Tool — Download invoice PDF from Zoho Books and save to OUTPUT_FOLDER.
Output filename: {source_file}_ZohoInvoice_{invoice_date}.pdf

Usage:
    Imported by orchestrator.py
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from zoho_client import zoho_get_pdf

load_dotenv()

OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "output")


def download_invoice_pdf(invoice_id: str, source_file: str, invoice_date: str) -> str:
    """
    Download invoice PDF from Zoho Books.
    Returns the saved file path.
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    pdf_bytes = zoho_get_pdf(f"/invoices/{invoice_id}")

    if not pdf_bytes:
        raise ValueError(f"Empty PDF response for invoice_id: {invoice_id}")

    filename  = f"{source_file}_ZohoInvoice_{invoice_date}.pdf"
    out_path  = os.path.join(OUTPUT_FOLDER, filename)

    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python tools/generate_pdf.py <invoice_id> <source_file> <invoice_date>")
        sys.exit(1)
    path = download_invoice_pdf(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Saved: {path}")
