from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Boolean
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    email         = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name  = Column(String, default="")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(String, default="")

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    jobs     = relationship("InvoiceJob",   back_populates="user", cascade="all, delete-orphan")
