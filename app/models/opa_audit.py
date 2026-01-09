import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base

class OPAAuditLog(Base):
    __tablename__ = "opa_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    project_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    
    policy_package: Mapped[str] = mapped_column(String, nullable=False) # e.g. procguard.approvals
    rule: Mapped[str] = mapped_column(String, nullable=False) # e.g. require_qp_signoff
    decision: Mapped[str] = mapped_column(String, nullable=False) # allow | deny
    
    resource_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. batch
    resource_id: Mapped[str] = mapped_column(String, nullable=True)
    
    input_hash: Mapped[str] = mapped_column(String, nullable=False) # sha256 of input facts
    result_hash: Mapped[str] = mapped_column(String, nullable=False) # sha256 of decision result
    decision_hash: Mapped[str] = mapped_column(String, nullable=False) # Root of trust: sha256(payload)
    
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=lambda: {})
    
    linked_violation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("violations.violation_id"), nullable=True)
    
    immutable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
