"""Fernet encryption for Zoho credentials stored in the database."""
import base64
import hashlib
from cryptography.fernet import Fernet
from ..config import SECRET_KEY


def _fernet() -> Fernet:
    # Derive a 32-byte key from SECRET_KEY
    key = base64.urlsafe_b64encode(
        hashlib.sha256(SECRET_KEY.encode()).digest()
    )
    return Fernet(key)


def encrypt(value: str) -> str:
    if not value:
        return ""
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    if not value:
        return ""
    try:
        return _fernet().decrypt(value.encode()).decode()
    except Exception:
        return ""   # bad key or unencrypted legacy value
