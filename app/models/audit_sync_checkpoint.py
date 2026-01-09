import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base

class AuditSyncCheckpoint(Base):
    __tablename__ = "audit_sync_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    stream_name: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g. "audit_logs", "events"
    
    # Checkpoint Data (Authoritative)
    last_event_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=True)
    last_event_hash: Mapped[str] = mapped_column(String, nullable=True)
    
    snapshot_hash: Mapped[str] = mapped_column(String, nullable=True)
    snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Identity & Verification
    verified_by: Mapped[str] = mapped_column(String, nullable=False, default="SYSTEM")
    signature: Mapped[str] = mapped_column(String, nullable=True) # Digital signature of this checkpoint

    # Replay/Recovery Mode
    is_recovery_checkpoint: Mapped[bool] = mapped_column(Boolean, default=False)
