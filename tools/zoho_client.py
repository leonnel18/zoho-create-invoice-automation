"""
zoho_client.py
Shared Zoho Books REST API client. Imported by all zoho_*.py tools.
Auth: OAuth2 refresh token flow.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
ORG_ID        = os.getenv("ZOHO_ORG_ID", "")
REGION        = os.getenv("ZOHO_REGION", "com")

TOKEN_URL = f"https://accounts.zoho.{REGION}/oauth/v2/token"
API_BASE  = f"https://www.zohoapis.{REGION}/books/v3"

# In-memory token cache — refreshed only when expired
_cached_token:      str   = ""
_token_expires_at:  float = 0.0


def get_access_token() -> str:
    """Return a valid access token, refreshing only when expired."""
    global _cached_token, _token_expires_at

    now = time.time()
    if _cached_token and now < _token_expires_at - 60:
        return _cached_token

    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "refresh_token",
    }
    resp = requests.post(TOKEN_URL, data=payload, timeout=15)
    resp.raise_for_status()
    data  = resp.json()
    token = data.get("access_token", "")
    if not token:
        raise ValueError(f"No access_token in response: {resp.text}")

    _cached_token     = token
    _token_expires_at = now + int(data.get("expires_in", 3600))
    return _cached_token


def _raise_with_body(resp: requests.Response):
    """Raise HTTPError with the Zoho response body included."""
    try:
        body = resp.json()
    except Exception:
        body = resp.text[:300]
    raise requests.HTTPError(
        f"{resp.status_code} {resp.reason} | Zoho: {body} | URL: {resp.url}",
        response=resp,
    )


def zoho_get(path: str, params: dict | None = None) -> dict:
    token   = get_access_token()
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    p       = {"organization_id": ORG_ID}
    if params:
        p.update(params)
    resp = requests.get(f"{API_BASE}{path}", headers=headers, params=p, timeout=15)
    if not resp.ok:
        _raise_with_body(resp)
    return resp.json()


def zoho_post(path: str, data: dict) -> dict:
    token   = get_access_token()
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type":  "application/json",
    }
    params = {"organization_id": ORG_ID}
    resp = requests.post(
        f"{API_BASE}{path}", headers=headers, params=params, json=data, timeout=15
    )
    if not resp.ok:
        _raise_with_body(resp)
    return resp.json()


def zoho_get_pdf(path: str) -> bytes:
    token   = get_access_token()
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    params  = {"organization_id": ORG_ID, "accept": "pdf"}
    resp    = requests.get(f"{API_BASE}{path}", headers=headers, params=params, timeout=30)
    if not resp.ok:
        _raise_with_body(resp)
    return resp.content
