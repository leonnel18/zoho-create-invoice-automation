"""
Seed the first user and import Zoho credentials from the project .env.

Run once:
    python -m web.backend.seed
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load project-level .env (contains ZOHO_* vars)
from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent.parent
load_dotenv(_project_root / ".env", override=False)

from .database import Base, engine, SessionLocal   # noqa: E402
from .models import User, UserSettings             # noqa: E402
from .core.security import hash_password           # noqa: E402
from .core.crypto import encrypt                   # noqa: E402
from .config import DATA_DIR                       # noqa: E402

SEED_EMAIL    = "gideon.valera@gmail.com"
SEED_PASSWORD = "ZohoAccount123"
SEED_NAME     = "Gino"


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == SEED_EMAIL).first()
        if existing:
            print(f"[seed] User {SEED_EMAIL} already exists — skipping.")
            return

        user = User(
            email=SEED_EMAIL,
            password_hash=hash_password(SEED_PASSWORD),
            display_name=SEED_NAME,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        db.add(user)
        db.flush()

        # Per-user data directories
        user_data = DATA_DIR / str(user.id)
        (user_data / "input").mkdir(parents=True, exist_ok=True)
        (user_data / "output").mkdir(parents=True, exist_ok=True)

        # Pull credentials from project .env (if present)
        client_id     = os.getenv("ZOHO_CLIENT_ID", "")
        client_secret = os.getenv("ZOHO_CLIENT_SECRET", "")
        refresh_token = os.getenv("ZOHO_REFRESH_TOKEN", "")
        org_id        = os.getenv("ZOHO_ORG_ID", "")
        region        = os.getenv("ZOHO_REGION", "com")
        item_rate     = float(os.getenv("DEFAULT_ITEM_RATE", "1.0"))
        default_cust  = os.getenv("DEFAULT_CUSTOMER", "Generic")

        # Respect existing INPUT/OUTPUT/DB paths from .env if set
        input_folder  = os.getenv("INPUT_FOLDER",  str(user_data / "input"))
        output_folder = os.getenv("OUTPUT_FOLDER", str(user_data / "output"))
        db_path       = os.getenv("DB_PATH",       str(user_data / "invoices.db"))

        settings = UserSettings(
            user_id=user.id,
            zoho_client_id=client_id,
            zoho_client_secret=encrypt(client_secret) if client_secret else "",
            zoho_refresh_token=encrypt(refresh_token) if refresh_token else "",
            zoho_org_id=org_id,
            zoho_region=region,
            input_folder=input_folder,
            output_folder=output_folder,
            db_path=db_path,
            default_item_rate=item_rate,
            default_customer=default_cust,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        db.add(settings)
        db.commit()
        print(f"[seed] Created user {SEED_EMAIL} (id={user.id})")
        if client_id:
            print(f"[seed] Zoho credentials imported from .env (org: {org_id})")
        else:
            print("[seed] No Zoho credentials in .env — configure via Settings page")
    finally:
        db.close()


if __name__ == "__main__":
    run()
