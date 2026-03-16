"""
rename_source.py
Layer 3 Tool — Rename a processed delivery receipt PDF.
Pattern: {original_name}_Invoice Generated_{YYYY-MM-DD}.pdf
Date used: today's processing date.

Usage:
    Imported by orchestrator.py
"""

import os
import sys
from datetime import date


def rename_source_file(pdf_path: str) -> str:
    """
    Rename the source PDF to mark it as processed.
    Returns the new file path.
    """
    directory  = os.path.dirname(pdf_path)
    basename   = os.path.basename(pdf_path)
    name, _ext = os.path.splitext(basename)
    today      = date.today().strftime("%Y-%m-%d")

    new_name   = f"{name}_Invoice Generated_{today}.pdf"
    new_path   = os.path.join(directory, new_name)

    os.rename(pdf_path, new_path)
    return new_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/rename_source.py <path_to_pdf>")
        sys.exit(1)
    new = rename_source_file(sys.argv[1])
    print(f"Renamed to: {new}")
