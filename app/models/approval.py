import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy import Uuid as UUID
from .base import Base

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batches.batch_id"), nullable=False)
    approver_id: Mapped[str] = mapped_column(String, nullable=False)
    approver_role: Mapped[str] = mapped_column(String, nullable=False)

    decision: Mapped[str] = mapped_column(String, nullable=False) # APPROVED, REJECTED
    reason: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(decision.in_(['APPROVED', 'REJECTED']), name='_approval_decision_check'),
    )
