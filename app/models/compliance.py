import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from .base import Base
from typing import List

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    evidence: Mapped[List["ComplianceEvidence"]] = relationship("ComplianceEvidence", back_populates="report", cascade="all, delete-orphan")

class ComplianceEvidence(Base):
    __tablename__ = "compliance_evidence"

    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("compliance_reports.id"), primary_key=True)
    blob_path: Mapped[str] = mapped_column(String, primary_key=True)
    evidence_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. "FILTER_AUDIT_TRAIL"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    report: Mapped["ComplianceReport"] = relationship("ComplianceReport", back_populates="evidence")
