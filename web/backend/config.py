import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_DIR  = Path(__file__).parent.parent.parent   # project root
WEB_DIR   = Path(__file__).parent.parent           # web/
TOOLS_DIR = BASE_DIR / "tools"
DATA_DIR  = BASE_DIR / "data" / "users"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY   = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM    = "HS256"
TOKEN_EXPIRE_HOURS = 24

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'web.db'}")

# Cloud deployment flags
CLOUD_MODE   = os.getenv("CLOUD_MODE", "false").lower() == "true"
FRONTEND_URL = os.getenv("FRONTEND_URL", "")  # e.g. https://your-app.vercel.app
