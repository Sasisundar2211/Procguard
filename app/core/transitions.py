from datetime import datetime
from sqlalchemy.orm import Session
from app.core.fsm import State, Event, ALLOWED_TRANSITIONS
from app.core.violations import (
    invalid_fsm_transition,
    terminal_state_mutation,
    progress_without_approval,
    approval_after_progress,
    duplicate_approval,
    unauthorized_approval,
    procedure_version_mismatch,
)

from app.models.batch import Batch
from app.models.event import BatchEvent
from app.models.violation import Violation
from app.models.audit import AuditLog
from app.security.rbac import authorize_event
from app.security.roles import Role
import uuid

def execute_transition(
    *,
    db: Session,
    batch: Batch,
    event: Event,
    actor: str,
    occurred_at: datetime,
    actor_role: str = "SUPERVISOR",
    approval_required: bool = False,
    approval_present: bool = False,
    already_progressed: bool = False,
    procedure_version: int | None = None,
):
    current_state = State(batch.current_state)

    # ========================================================
    # SINGLE AUDIT GUARANTEE
    # ========================================================
    def violate(rule: str, outcome: str):
        from app.core.violations_handler import resolve_sop_for_rule, handle_violation_enforcement
        from app.core.opa import record_opa_decision
        from app.core.crypto import canonical_hash
        
        batch.current_state = State.VIOLATED.value

        # 1. Record OPA Decision (Root of Truth)
        opa_log = record_opa_decision(
            db=db,
            policy_package="procguard.lifecycle", # Simplified for MVP
            rule=rule,
            decision="deny",
            resource_type="batch",
            resource_id=str(batch.batch_id),
            input_facts={
                "current_state": current_state.value,
                "event": event.value,
                "actor_role": actor_role
            },
            project_id=batch.project_id if hasattr(batch, 'project_id') else uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        )

        # 2. Resolve SOP (Part 1.3)
        sop = resolve_sop_for_rule(db, rule)
        
        # 3. Create Violation with OPA Hash Linkage (Step 3)
        violation_payload = {
            "violation_type": rule,
            "batch_id": str(batch.batch_id),
            "opa_decision_hash": opa_log.decision_hash,
            "detected_at": occurred_at.isoformat()
        }
        v_hash = canonical_hash(violation_payload)

        violation = Violation(
            batch_id=batch.batch_id,
            rule=rule,
            detected_at=occurred_at,
            sop_id=sop.id if sop else None,
            opa_decision_hash=opa_log.decision_hash,
            violation_hash=v_hash,
            payload=violation_payload
        )
        db.add(violation)
        db.flush() 

        # 4. Deterministic Resolution & Evidence Chaining (Part 1, 2, 3)
        handle_violation_enforcement(db=db, violation=violation, actor_id=actor)

        # 5. Create Audit Log Entry with Violation Hash Link (Step 4)
        audit_payload = {
            "action": event.value,
            "violation_hash": v_hash,
            "actor": actor,
            "resource": str(batch.batch_id),
            "timestamp": occurred_at.isoformat()
        }
        a_hash = canonical_hash(audit_payload)

        db.add(
            AuditLog(
                batch_id=batch.batch_id,
                expected_state=current_state.value,
                actual_state=current_state.value,  # State didn't change
                action=event.value,
                result="FAILURE",
                project="ProcGuard Core",
                actor=actor,
                timestamp=occurred_at,
                client="API",
                agent="PROCguard",
                violation_id=violation.id,
                audit_hash=a_hash,
                violation_hash_link=v_hash,
                payload=audit_payload
            )
        )

        db.commit()
        raise RuntimeError(rule)

    # ========================================================
    # 1. AUTHORIZATION (MUST BE FIRST)
    # ========================================================
    authorize_event(
        role=Role(actor_role),
        event=event,
    )

    # ========================================================
    # 2. TERMINAL STATES — ABSOLUTE
    # ========================================================
    if terminal_state_mutation(current_state):
        violate("TERMINAL_STATE_MUTATION", "REJECTED_TERMINAL_STATE")

    # ========================================================
    # 3. FSM STRUCTURAL CLOSURE (NO GAPS)
    # ========================================================
    if (current_state, event) not in ALLOWED_TRANSITIONS:
        violate("INVALID_FSM_TRANSITION", "VIOLATION_INVALID_TRANSITION")

    # ========================================================
    # 4. PROCEDURE IMMUTABILITY
    # ========================================================
    if procedure_version is not None and procedure_version_mismatch(
        batch.procedure_version,
        procedure_version,
    ):
        violate("PROCEDURE_VERSION_MISMATCH", "VIOLATION_PROCEDURE_VERSION")

    # ========================================================
    # 5. APPROVAL INVARIANTS
    # ========================================================
    if event == Event.APPROVE_STEP:
        if unauthorized_approval(actor_role):
            violate("UNAUTHORIZED_APPROVAL", "VIOLATION_UNAUTHORIZED_APPROVAL")

        if approval_after_progress(event, already_progressed):
            violate("APPROVAL_AFTER_PROGRESS", "VIOLATION_LATE_APPROVAL")

        if duplicate_approval(approval_present):
            violate("DUPLICATE_APPROVAL", "VIOLATION_DUPLICATE_APPROVAL")

    # ========================================================
    # 6. OTHER INVARIANTS
    # ========================================================
    if progress_without_approval(event, approval_required, approval_present):
        violate("PROGRESS_WITHOUT_APPROVAL", "VIOLATION_MISSING_APPROVAL")

    # 8. VALID TRANSITION (EXACTLY ONE SUCCESS AUDIT)
    next_state = ALLOWED_TRANSITIONS[(current_state, event)]
    batch.current_state = next_state.value

    from app.core.crypto import canonical_hash

    db.add(
        BatchEvent(
            batch_id=batch.batch_id,
            event_type=event.value,
            payload={},
            occurred_at=occurred_at,
        )
    )

    success_payload = {
        "action": event.value,
        "expected_state": current_state.value,
        "actual_state": next_state.value,
        "actor": actor,
        "timestamp": occurred_at.isoformat()
    }
    s_hash = canonical_hash(success_payload)

    db.add(
        AuditLog(
            batch_id=batch.batch_id,
            expected_state=current_state.value,
            actual_state=next_state.value, # State changed
            action=event.value,
            result="SUCCESS",
            project="ProcGuard Core",
            actor=actor,
            timestamp=occurred_at,
            client="API",
            agent="PROCguard",
            violation_id=None,
            audit_hash=s_hash,
            payload=success_payload
        )
    )

    db.commit()
