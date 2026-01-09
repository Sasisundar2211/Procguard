import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base
from .batch import Batch
from .sop import SOP

class Violation(Base):
    __tablename__ = "violations"

    # Standardize to 'id' for consistency with authoritative patterns
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4, name="violation_id")
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batches.batch_id"))
    rule: Mapped[str] = mapped_column(String, nullable=False) # e.g. INVALID_FSM_TRANSITION
    sop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sops.id"), nullable=True) # Will be NOT NULL after data seeding
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    # Authoritative Hash Chain (Step 3)
    violation_hash: Mapped[str] = mapped_column(String, nullable=True) # sha256(payload)
    opa_decision_hash: Mapped[str] = mapped_column(String, nullable=True) # Links back to policy root
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=lambda: {})

    # Audit-safe status: OPEN, RESOLVED
    status: Mapped[str] = mapped_column(String, nullable=False, default="OPEN")

    # Cross-link to filter context at detection (Part 3)
    triggering_filter_event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("filter_audit_logs.id"), nullable=True)

    batch: Mapped["Batch"] = relationship("Batch")
    filter_context: Mapped["FilterAuditLog"] = relationship("FilterAuditLog")
    sop: Mapped["SOP"] = relationship("SOP")
