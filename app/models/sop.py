import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy import Uuid as UUID, JSON as JSONB
from .base import Base
from typing import List

class SOP(Base):
    __tablename__ = "sops"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    immutable_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    rules: Mapped[List["SOPRule"]] = relationship("SOPRule", back_populates="sop")
    enforcement_actions: Mapped[List["EnforcementAction"]] = relationship("EnforcementAction", back_populates="sop")

class SOPRule(Base):
    __tablename__ = "sop_rules"

    sop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sops.id"), primary_key=True)
    rule_code: Mapped[str] = mapped_column(String, primary_key=True)

    sop: Mapped["SOP"] = relationship("SOP", back_populates="rules")

class EnforcementAction(Base):
    __tablename__ = "enforcement_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    sop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sops.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False) # LOCK_PROCEDURE, etc.
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    sop: Mapped["SOP"] = relationship("SOP", back_populates="enforcement_actions")

class EnforcementEvent(Base):
    __tablename__ = "enforcement_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    violation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("violations.violation_id"), nullable=False)
    sop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sops.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    executed_by: Mapped[str] = mapped_column(String, default="SYSTEM")
    outcome: Mapped[str] = mapped_column(String)

class EvidenceChain(Base):
    __tablename__ = "evidence_chain"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    violation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("violations.violation_id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False) # FILTER_APPLIED, VIOLATION_DETECTED, etc.
    source_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    hash: Mapped[str] = mapped_column(String, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
