from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from ..database import Base


class InvoiceJob(Base):
    __tablename__ = "invoice_jobs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    triggered_by    = Column(String, default="manual")   # manual | watcher
    status          = Column(String, default="running")  # running | done | error
    pdf_filename    = Column(String, nullable=True)
    log_output      = Column(Text, nullable=True)
    invoices_pushed = Column(Integer, default=0)
    errors          = Column(Integer, default=0)
    started_at      = Column(String, default="")
    finished_at     = Column(String, nullable=True)

    user = relationship("User", back_populates="jobs")
