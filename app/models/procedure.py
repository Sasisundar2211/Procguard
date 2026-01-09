import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy import Uuid as UUID
from typing import List
from .base import Base

class Procedure(Base):
    __tablename__ = "procedures"

    procedure_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


    steps: Mapped[List["ProcedureStep"]] = relationship("ProcedureStep", back_populates="procedure", cascade="all, delete-orphan", order_by="ProcedureStep.step_order")

class ProcedureStep(Base):
    __tablename__ = "procedure_steps"

    step_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    procedure_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procedures.procedure_id"))
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approver_role: Mapped[str] = mapped_column(String, nullable=True)

    procedure: Mapped["Procedure"] = relationship("Procedure", back_populates="steps")

    __table_args__ = (
        UniqueConstraint('procedure_id', 'step_order', name='_procedure_step_order_uc'),
    )