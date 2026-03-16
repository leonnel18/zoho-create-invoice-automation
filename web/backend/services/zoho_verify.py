"""Verify Zoho credentials by hitting a lightweight API endpoint."""
import requests


def verify_zoho_credentials(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    org_id: str,
    region: str = "com",
) -> tuple[bool, str]:
    """
    Try to get a fresh access token and call GET /items?per_page=1.
    Returns (ok: bool, message: str).
    """
    # Step 1 — exchange refresh token for access token
    token_url = f"https://accounts.zoho.{region}/oauth/v2/token"
    try:
        r = requests.post(
            token_url,
            data={
                "grant_type":    "refresh_token",
                "client_id":     client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        return False, f"Token request failed: {exc}"

    access_token = data.get("access_token")
    if not access_token:
        error = data.get("error", "unknown")
        return False, f"Token error: {error}"

    # Step 2 — call a lightweight Zoho Books endpoint
    api_url = f"https://www.zohoapis.{region}/books/v3/items"
    try:
        resp = requests.get(
            api_url,
            params={"organization_id": org_id, "per_page": "1"},
            headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        body = resp.json()
    except Exception as exc:
        return False, f"API call failed: {exc}"

    code = body.get("code", -1)
    if code != 0:
        return False, body.get("message", "Zoho API returned non-zero code")

    return True, "Credentials verified successfully"
