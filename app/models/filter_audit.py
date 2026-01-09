import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base

class FilterAuditLog(Base):
    __tablename__ = "filter_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    screen: Mapped[str] = mapped_column(String, nullable=False) # e.g. "AUDIT_LOGS"
    filter_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    prev_hash: Mapped[str] = mapped_column(String, nullable=True)
    hash: Mapped[str] = mapped_column(String, nullable=False)
