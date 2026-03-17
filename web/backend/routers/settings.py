from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserSettings
from ..schemas.settings import SettingsRead, SettingsUpdate
from ..core.dependencies import get_current_user
from ..core.crypto import encrypt, decrypt
from ..services.zoho_verify import verify_zoho_credentials

router = APIRouter(prefix="/api/settings", tags=["settings"])

MASKED = "••••••••"


def _mask(value: str) -> str:
    return MASKED if value else ""


def _read_settings(s: UserSettings) -> dict:
    return {
        "zoho_client_id":     s.zoho_client_id,
        "zoho_client_secret": _mask(s.zoho_client_secret),
        "zoho_refresh_token": _mask(s.zoho_refresh_token),
        "zoho_org_id":        s.zoho_org_id,
        "zoho_region":        s.zoho_region,
        "input_folder":       s.input_folder,
        "output_folder":      s.output_folder,
        "db_path":            s.db_path,
        "default_item_rate":  s.default_item_rate,
        "default_customer":   s.default_customer,
        "dedup_enabled":      s.dedup_enabled if s.dedup_enabled is not None else True,
        "watch_enabled":      s.watch_enabled,
        "last_watch_event":   s.last_watch_event,
    }


@router.get("", response_model=SettingsRead)
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s:
        raise HTTPException(404, "Settings not found")
    return _read_settings(s)


@router.put("", response_model=SettingsRead)
def update_settings(
    body: SettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request=None,
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s:
        raise HTTPException(404, "Settings not found")

    if body.zoho_client_id     is not None: s.zoho_client_id     = body.zoho_client_id
    if body.zoho_org_id        is not None: s.zoho_org_id        = body.zoho_org_id
    if body.zoho_region        is not None: s.zoho_region        = body.zoho_region
    if body.input_folder       is not None: s.input_folder       = body.input_folder
    if body.output_folder      is not None: s.output_folder      = body.output_folder
    if body.db_path            is not None: s.db_path            = body.db_path
    if body.default_item_rate  is not None: s.default_item_rate  = body.default_item_rate
    if body.default_customer   is not None: s.default_customer   = body.default_customer
    if body.dedup_enabled      is not None: s.dedup_enabled      = body.dedup_enabled
    if body.watch_enabled      is not None: s.watch_enabled      = body.watch_enabled

    # Encrypt sensitive fields only when new values are provided (not masked placeholders)
    if body.zoho_client_secret and body.zoho_client_secret != MASKED:
        s.zoho_client_secret = encrypt(body.zoho_client_secret)
    if body.zoho_refresh_token and body.zoho_refresh_token != MASKED:
        s.zoho_refresh_token = encrypt(body.zoho_refresh_token)

    s.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    return _read_settings(s)


@router.post("/verify")
def verify_credentials(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not s or not s.zoho_client_id:
        raise HTTPException(400, "No credentials saved yet")

    ok, message = verify_zoho_credentials(
        client_id=s.zoho_client_id,
        client_secret=decrypt(s.zoho_client_secret),
        refresh_token=decrypt(s.zoho_refresh_token),
        org_id=s.zoho_org_id,
        region=s.zoho_region or "com",
    )
    return {"ok": ok, "message": message}
