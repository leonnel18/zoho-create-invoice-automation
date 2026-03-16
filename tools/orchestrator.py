"""
orchestrator.py
Layer 2 Navigation — Main pipeline runner.
Scans INPUT_FOLDER, processes each unhandled PDF end-to-end.

One PDF may yield multiple invoices (one per customer found in the file).
The source PDF is renamed only after ALL its invoices are successfully pushed.

Trigger:
    Manual : run_pipeline.bat
    Cron   : Windows Task Scheduler (daily 6PM)

Usage:
    python tools/orchestrator.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from parse_pdf     import parse_pdf
from db_store      import init_db, get_status, insert_invoice, update_pushed, update_pdf_path, update_error
from zoho_push     import push_invoice
from generate_pdf  import download_invoice_pdf
from rename_source import rename_source_file

load_dotenv()

INPUT_FOLDER = os.getenv("INPUT_FOLDER", "input")
SKIP_MARKER  = "_Invoice Generated_"


def get_pdf_files() -> list:
    if not os.path.isdir(INPUT_FOLDER):
        raise FileNotFoundError(f"INPUT_FOLDER not found: {INPUT_FOLDER}")
    return [
        os.path.join(INPUT_FOLDER, f)
        for f in os.listdir(INPUT_FOLDER)
        if f.lower().endswith(".pdf") and SKIP_MARKER not in f
    ]


def process_invoice(invoice: dict) -> bool:
    """
    Run the full pipeline for a single invoice dict.
    Returns True on success, False on error.
    """
    source_file   = invoice["source_file"]
    customer_name = invoice["customer_name"]

    # Skip if already successfully pushed
    if get_status(source_file) == "pushed":
        print(f"    [SKIP] Already pushed: {customer_name}")
        return True

    print(f"    [>>>] Customer : {customer_name}")
    print(f"          Date     : {invoice['date']}")
    print(f"          Items    : {len(invoice['items'])}")

    try:
        insert_invoice(invoice)

        zoho_invoice_id = push_invoice(invoice)
        print(f"          Zoho ID  : {zoho_invoice_id}")

        update_pushed(source_file, zoho_invoice_id)

        pdf_out = download_invoice_pdf(zoho_invoice_id, source_file.replace("::", "_"), invoice["date"])
        print(f"          PDF out  : {os.path.basename(pdf_out)}")

        update_pdf_path(source_file, pdf_out)
        return True

    except Exception as e:
        print(f"          [ERROR]  : {e}")
        update_error(source_file, str(e))
        return False


def process_pdf(pdf_path: str) -> tuple:
    """
    Parse and process all invoices in a single PDF.
    Returns (success_count, error_count).
    Renames source PDF only if all invoices succeeded.
    """
    filename = os.path.basename(pdf_path)
    print(f"\n  [FILE] {filename}")

    try:
        invoices = parse_pdf(pdf_path)
    except Exception as e:
        print(f"    [ERROR] Parse failed: {e}")
        return 0, 1

    print(f"         {len(invoices)} invoice(s) found\n")

    success, errors = 0, 0
    for invoice in invoices:
        ok = process_invoice(invoice)
        if ok:
            success += 1
        else:
            errors += 1

    # Rename source PDF only when all invoices from it are done
    if errors == 0:
        try:
            new_path = rename_source_file(pdf_path)
            print(f"\n    [RENAMED] {os.path.basename(new_path)}")
        except Exception as e:
            print(f"\n    [WARN] Rename failed: {e}")

    return success, errors


def run():
    init_db()
    print("=" * 60)
    print("Zoho Invoice Pipeline — Starting")
    print(f"Input folder: {INPUT_FOLDER}")
    print("=" * 60)

    try:
        pdf_files = get_pdf_files()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if not pdf_files:
        print("No new PDFs to process.")
        return

    print(f"Found {len(pdf_files)} PDF file(s).")

    total_success, total_errors = 0, 0
    for pdf_path in pdf_files:
        s, e = process_pdf(pdf_path)
        total_success += s
        total_errors  += e

    print("\n" + "=" * 60)
    print(f"Done. Invoices pushed: {total_success} | Errors: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    run()
