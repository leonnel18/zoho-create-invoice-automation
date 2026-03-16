"""
generate_refresh_token.py
One-time script — exchange a Self Client grant code for a refresh token.
Run this once, copy ZOHO_REFRESH_TOKEN into .env, then never run again.

Usage:
    python tools/generate_refresh_token.py <grant_code>
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
TOKEN_URL     = "https://accounts.zoho.com/oauth/v2/token"


def generate(grant_code: str):
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[ERROR] ZOHO_CLIENT_ID or ZOHO_CLIENT_SECRET not set in .env")
        return

    payload = {
        "code":          grant_code,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri":  "https://www.zoho.com/books",
        "grant_type":    "authorization_code",
    }

    print(f"Exchanging grant code with {TOKEN_URL}...\n")
    resp = requests.post(TOKEN_URL, data=payload, timeout=15)

    if resp.status_code == 200:
        data = resp.json()
        if "refresh_token" in data:
            print("✅ SUCCESS\n")
            print(f"  Access Token  : {data.get('access_token', '')[:30]}...")
            print(f"  Refresh Token : {data['refresh_token']}")
            print(f"  Expires In    : {data.get('expires_in')}s\n")
            print("─" * 60)
            print("Add this to your .env:")
            print(f"  ZOHO_REFRESH_TOKEN={data['refresh_token']}")
            print("─" * 60)
        else:
            print(f"[FAIL] No refresh token in response:\n{data}")
    else:
        print(f"[FAIL] {resp.status_code}: {resp.text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/generate_refresh_token.py <grant_code>")
        sys.exit(1)
    generate(sys.argv[1])
