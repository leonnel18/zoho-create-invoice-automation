from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL

# Supabase (and some tools) give "postgres://" but SQLAlchemy 2.x requires "postgresql://"
_db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_is_sqlite = _db_url.startswith("sqlite")

engine = create_engine(
    _db_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    # Keep pool small on Supabase free tier (max 10 connections)
    **({} if _is_sqlite else {"pool_size": 3, "max_overflow": 2}),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
