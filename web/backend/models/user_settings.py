from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from ..database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Zoho credentials (client_secret + refresh_token stored encrypted)
    zoho_client_id     = Column(String, default="")
    zoho_client_secret = Column(String, default="")
    zoho_refresh_token = Column(String, default="")
    zoho_org_id        = Column(String, default="")
    zoho_region        = Column(String, default="com")

    # Folder paths
    input_folder  = Column(String, default="")
    output_folder = Column(String, default="")
    db_path       = Column(String, default="")

    # Pipeline defaults
    default_item_rate = Column(Float, default=1.0)
    default_customer  = Column(String, default="Generic")
    dedup_enabled     = Column(Boolean, default=True)

    # Watcher state
    watch_enabled    = Column(Boolean, default=True)
    last_watch_event = Column(String, nullable=True)

    updated_at = Column(String, default="")

    user = relationship("User", back_populates="settings")
