"""
verify_zoho.py
Phase 2: Link — Verify Zoho Books REST API connection.
Auto-detects correct Zoho region by trying all token endpoints.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
ORG_ID        = os.getenv("ZOHO_ORG_ID", "")

REGIONS = [
    ("com",    "https://accounts.zoho.com/oauth/v2/token",    "https://www.zohoapis.com/books/v3"),
    ("com.au", "https://accounts.zoho.com.au/oauth/v2/token", "https://www.zohoapis.com.au/books/v3"),
    ("in",     "https://accounts.zoho.in/oauth/v2/token",     "https://www.zohoapis.in/books/v3"),
    ("eu",     "https://accounts.zoho.eu/oauth/v2/token",     "https://www.zohoapis.eu/books/v3"),
]


def get_access_token(token_url: str) -> str | None:
    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "refresh_token",
    }
    try:
        resp = requests.post(token_url, data=payload, timeout=15)
        print(f"  [{resp.status_code}] {token_url}")
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            if token:
                return token
            print(f"  [WARN] 200 but no access_token in response: {resp.text[:200]}")
        else:
            print(f"         {resp.text[:150]}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERR] {e}")
    return None


def verify_connection() -> bool:
    missing = [k for k, v in {
        "ZOHO_CLIENT_ID":     CLIENT_ID,
        "ZOHO_CLIENT_SECRET": CLIENT_SECRET,
        "ZOHO_REFRESH_TOKEN": REFRESH_TOKEN,
        "ZOHO_ORG_ID":        ORG_ID,
    }.items() if not v]

    if missing:
        print(f"[ERROR] Missing in .env: {', '.join(missing)}")
        return False

    print("Step 1: Trying all regions for access token...\n")

    token    = None
    api_base = None

    for region, token_url, books_url in REGIONS:
        token = get_access_token(token_url)
        if token:
            api_base = books_url
            print(f"\n  ✅ Token OK on region: {region}")
            print(f"     Add to .env: ZOHO_REGION={region}\n")
            break

    if not token or not api_base:
        print("\n[FAIL] Could not obtain access token on any region.")
        print("Check ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN in .env.")
        return False

    headers = {"Authorization": f"Zoho-oauthtoken {token}"}

    print("Step 2: Listing accessible Zoho Books organizations...")
    try:
        resp = requests.get(f"{api_base}/organizations", headers=headers, timeout=15)
        if resp.status_code == 200:
            orgs = resp.json().get("organizations", [])
            print(f"  [OK] {len(orgs)} organization(s) found:\n")
            for org in orgs:
                match = " ← matches .env" if org.get("organization_id") == ORG_ID else ""
                print(f"       {org.get('name')} | org_id: {org.get('organization_id')}{match}")
            if not any(o.get("organization_id") == ORG_ID for o in orgs):
                print(f"\n  [WARN] ZOHO_ORG_ID '{ORG_ID}' not in list above — update .env with correct org_id")
                return False
        else:
            print(f"  [FAIL] {resp.status_code}: {resp.text[:300]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  [ERR] {e}")
        return False

    print(f"\nStep 3: Probing Zoho Books items (org: {ORG_ID})...")
    params = {"organization_id": ORG_ID, "per_page": 1}
    try:
        resp = requests.get(f"{api_base}/items", headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            print(f"  [OK] Connected. Items in response: {len(items)}")
            if items:
                print(f"       Sample: {items[0].get('name')} (id: {items[0].get('item_id')})")
            print("\n✅ Zoho Books REST API: VERIFIED")
            return True
        else:
            print(f"  [FAIL] {resp.status_code}: {resp.text[:300]}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERR] {e}")

    return False


if __name__ == "__main__":
    ok = verify_connection()
    exit(0 if ok else 1)
