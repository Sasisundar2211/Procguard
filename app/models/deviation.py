import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean, CheckConstraint
from sqlalchemy import Uuid as UUID
from .base import Base

class Deviation(Base):
    __tablename__ = "deviations"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batches.batch_id"), nullable=False)
    stage: Mapped[str] = mapped_column(String, nullable=False)
    deviation_type: Mapped[str] = mapped_column(String, nullable=False) # TIME, SEQUENCE, RULE
    
    approved_by: Mapped[str] = mapped_column(String, nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    valid_from_day: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_until_day: Mapped[int] = mapped_column(Integer, nullable=False)
    
    superseded_by_lir: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(deviation_type.in_(['TIME', 'SEQUENCE', 'RULE']), name='_deviation_type_check'),
    )
