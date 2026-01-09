import uuid
import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base
from .batch import Batch
from .violation import Violation

class AuditSource(str, enum.Enum):
    SYSTEM = "SYSTEM"
    OPA = "OPA"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    source: Mapped[str] = mapped_column(String, nullable=False, default="SYSTEM")
    project_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False, default=lambda: uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))
    event_type: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[str] = mapped_column(String, nullable=True)
    client_id: Mapped[str] = mapped_column(String, nullable=False, default="API")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=lambda: {})
    
    # Authoritative Hash Chain (Step 4)
    audit_hash: Mapped[str] = mapped_column(String, nullable=True) # sha256(payload)
    violation_hash_link: Mapped[str] = mapped_column(String, nullable=True) # Matches violation.violation_hash

    # Forensic Metadata (standardized across migrations)
    actor: Mapped[str] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=True)
    result: Mapped[str] = mapped_column(String, nullable=True)
    
    expected_state: Mapped[str] = mapped_column(String, nullable=True)
    actual_state: Mapped[str] = mapped_column(String, nullable=True)
    project: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    client: Mapped[str] = mapped_column(String, nullable=True)
    agent: Mapped[str] = mapped_column(String, nullable=True)

    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batches.batch_id"), nullable=True)
    violation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("violations.violation_id"), nullable=True)

    batch: Mapped["Batch"] = relationship("Batch")
    violation: Mapped["Violation"] = relationship("Violation")
