"""
zoho_push.py
Layer 3 Tool — Push a parsed invoice to Zoho Books.
Handles: customer lookup/create, item lookup/create, invoice creation.
Returns: zoho_invoice_id (str)

Usage:
    Imported by orchestrator.py
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from zoho_client import zoho_get, zoho_post

load_dotenv()

DEFAULT_RATE = float(os.getenv("DEFAULT_ITEM_RATE", "1.00"))


# ── Customer ─────────────────────────────────────────────────────────────────

def get_or_create_customer(name: str) -> str:
    """Return Zoho contact_id for the given customer name. Creates if missing."""
    data = zoho_get("/contacts", {"search_text": name})
    for contact in data.get("contacts", []):
        if contact.get("contact_name", "").strip().lower() == name.lower():
            return contact["contact_id"]

    # Not found — create
    payload = {"contact_name": name, "contact_type": "customer"}
    result  = zoho_post("/contacts", payload)
    return result["contact"]["contact_id"]


# ── Items ─────────────────────────────────────────────────────────────────────

def get_or_create_item(item_name: str, unit: str) -> str:
    """Return Zoho item_id for the given item name. Creates if missing."""
    data = zoho_get("/items", {"search_text": item_name})
    for item in data.get("items", []):
        if item.get("name", "").strip().lower() == item_name.lower():
            return item["item_id"]

    # Not found — create (try with unit, fallback without if rejected)
    payload = {"name": item_name, "rate": DEFAULT_RATE, "unit": unit}
    try:
        result = zoho_post("/items", payload)
        return result["item"]["item_id"]
    except Exception:
        # Retry without unit (some unit strings may be invalid in Zoho)
        payload_no_unit = {"name": item_name, "rate": DEFAULT_RATE}
        result = zoho_post("/items", payload_no_unit)
        return result["item"]["item_id"]


# ── Invoice ───────────────────────────────────────────────────────────────────

def push_invoice(parsed: dict) -> str:
    """
    Push a parsed invoice dict to Zoho Books.
    Returns zoho_invoice_id.
    """
    customer_id = get_or_create_customer(parsed["customer_name"])

    line_items = []
    for item in parsed["items"]:
        item_id = get_or_create_item(item["item_name"], item.get("unit", ""))
        line_items.append({
            "item_id":  item_id,
            "name":     item["item_name"],
            "quantity": item["qty"],
            "unit":     item.get("unit", ""),
            "rate":     DEFAULT_RATE,
        })

    invoice_date = datetime.strptime(parsed["date"], "%Y-%m-%d")
    due_date     = (invoice_date + timedelta(days=15)).strftime("%Y-%m-%d")

    payload = {
        "customer_id":      customer_id,
        "date":             parsed["date"],
        "txn_posting_date": parsed["date"],
        "due_date":         due_date,
        "line_items":       line_items,
    }

    result = zoho_post("/invoices", payload)
    return result["invoice"]["invoice_id"]


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/zoho_push.py path/to/parsed.json")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    invoice_id = push_invoice(data)
    print(f"Invoice created: {invoice_id}")
