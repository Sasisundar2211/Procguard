from app.enforcement.engine import run_enforcement
from app.enforcement.approval_gate import can_batch_progress
from app.core.audit import write_audit_log
from sqlalchemy.orm import Session
import logging

# Set up logging for auditability
logger = logging.getLogger("procguard.execution")

def load_sop_for_batch(batch_id):
    """Placeholder: Load SOP from DB."""
    return {
        "id": "sop_001",
        "steps": [
            {"id": "step_1", "name": "Start"},
            {"id": "step_2", "name": "Process"},
            {"id": "step_3", "name": "End"}
        ]
    }

def load_role_map(sop_id):
    """Placeholder: Load role map for SOP."""
    return {
        "step_2": "SUPERVISOR",
        "step_3": "OPERATOR"
    }

def record_violation(db: Session, batch_id: str, violation: dict):
    """Record violation in DB and Audit Log."""
    logger.warning(f"VIOLATION DETECTED for Batch {batch_id}: {violation}")
    write_audit_log(
        db=db,
        action="VIOLATION_DETECTED",
        batch_id=batch_id,
        result="FAILED",
        metadata=violation,
        actual_state="PENDING_APPROVAL"
    )

def process_execution(db: Session, batch_id: str, execution_events: list, actor_id: str):
    """
    Authoritative processing of execution data.
    Ensures deterministic enforcement AND approval gates before state changes.
    """
    sop = load_sop_for_batch(batch_id)
    role_map = load_role_map(sop["id"])

    # 1. Run Deterministic Validators
    violation = run_enforcement(
        sop_steps=sop["steps"],
        execution_events=execution_events,
        role_map=role_map
    )

    if violation:
        record_violation(db, batch_id, violation)
        # Lock batch state to PENDING_APPROVAL
        return {"status": "BLOCKED", "violation": violation}

    # 2. Check Approval Gate (Hard Enforcement)
    if not can_batch_progress(db, batch_id):
        logger.info(f"Progress BLOCKED for Batch {batch_id}: Approval Required")
        write_audit_log(
            db=db,
            action="PROGRESS_ATTEMPTED",
            batch_id=batch_id,
            result="DENIED",
            actor=actor_id,
            metadata={"detail": "Approval gate required"}
        )
        raise PermissionError("Approval required before progress can continue")

    # 3. Success Flow
    logger.info(f"Progress ALLOWED for Batch {batch_id}")
    write_audit_log(
        db=db,
        action="PROGRESS_ALLOWED",
        batch_id=batch_id,
        result="SUCCESS",
        actor=actor_id,
        actual_state="CONTINUE"
    )
    return {"status": "SUCCESS"}
