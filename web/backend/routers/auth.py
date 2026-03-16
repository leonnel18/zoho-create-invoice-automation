from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserSettings
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from ..core.security import hash_password, verify_password, create_access_token
from ..core.dependencies import get_current_user
from ..config import DATA_DIR

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name or body.email.split("@")[0],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(user)
    db.flush()  # get user.id before commit

    # Create default per-user data directories and settings row
    user_data = DATA_DIR / str(user.id)
    (user_data / "input").mkdir(parents=True, exist_ok=True)
    (user_data / "output").mkdir(parents=True, exist_ok=True)

    settings = UserSettings(
        user_id=user.id,
        input_folder=str(user_data / "input"),
        output_folder=str(user_data / "output"),
        db_path=str(user_data / "invoices.db"),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(settings)
    db.commit()

    return TokenResponse(access_token=create_access_token(user.id, user.email))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return TokenResponse(access_token=create_access_token(user.id, user.email))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
