from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.api.deps import get_db
from app.models.batch import Batch
from app.models.violation import Violation
from app.core.fsm import State

router = APIRouter()

class BoardResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    color: str
    href: str
    primary_label: Optional[str] = None
    primary_count: Optional[int] = 0
    secondary_label: Optional[str] = None
    secondary_count: Optional[int] = 0
    is_system: bool
    status: str

@router.get("/", response_model=List[BoardResponse])
def get_boards(db: Session = Depends(get_db)):
    """
    Get dynamic dashboard boards (swimlanes/summaries).
    Driven by backend state for perfect mapping.
    """
    from app.models.procedure import Procedure
    # Evidence might be a table or just audit logs. For now we use a placeholder or count audit logs.
    from app.models.audit import AuditLog

    # 1. Procedures
    proc_count = db.query(Procedure).count()

    # 2. Batches
    total_batches = db.query(Batch).count()
    completed_batches = db.query(Batch).filter(Batch.current_state == State.COMPLETED.value).count()

    # 3. Violations
    violation_count = db.query(Violation).count()
    resolved_violations = db.query(Violation).filter(Violation.status == 'RESOLVED').count()

    # 4. Evidence (Audit Logs as proxy for now)
    evidence_count = db.query(AuditLog).count()

    boards = [
        BoardResponse(
            id="sys-procedures",
            title="Procedure",
            description="Active Standard Operating Procedures",
            color="bg-slate-600",
            href="/procedures",
            primary_label="Active",
            primary_count=proc_count,
            secondary_label="Pending",
            secondary_count=0,
            is_system=True,
            status="ACTIVE"
        ),
        BoardResponse(
            id="sys-batches",
            title="Batch State",
            description="Manufacturing Batch Execution",
            color="bg-blue-600",
            href="/batches",
            primary_label="Total",
            primary_count=total_batches,
            secondary_label="Completed",
            secondary_count=completed_batches,
            is_system=True,
            status="ACTIVE"
        ),
        BoardResponse(
            id="sys-violations",
            title="Violation",
            description="Detected Compliance Violations",
            color="bg-red-600",
            href="/violations",
            primary_label="Violated",
            primary_count=violation_count,
            secondary_label="Resolved",
            secondary_count=resolved_violations,
            is_system=True,
            status="ACTIVE"
        ),
        BoardResponse(
            id="sys-evidence",
            title="Audit Evidence",
            description="Cryptographic Evidence Chain",
            color="bg-emerald-600",
            href="/system/audit-logs",
            primary_label="Items",
            primary_count=evidence_count,
            secondary_label="Reviews",
            secondary_count=0,
            is_system=True,
            status="ACTIVE"
        )
    ]
    
    return boards
