from sqlalchemy.orm import Session
from app.models.violation import Violation
from app.models.sop import SOP, SOPRule, EnforcementAction, EnforcementEvent
from app.core.evidence import add_evidence_node
from app.core.filter_audit import FilterAuditLog
from sqlalchemy import desc
import uuid
from datetime import datetime, timezone

def resolve_sop_for_rule(db: Session, rule_code: str) -> SOP | None:
    """Deterministic SOP Resolution."""
    sop_mapping = db.query(SOPRule).filter(SOPRule.rule_code == rule_code).first()
    if not sop_mapping:
        return None
    return db.query(SOP).filter(SOP.id == sop_mapping.sop_id, SOP.is_active == True).first()

def handle_violation_enforcement(
    db: Session,
    violation: Violation,
    actor_id: str
):
    """
    Executes enforcement and builds evidence chain.
    """
    if not violation.sop_id:
        return

    sop = db.query(SOP).filter(SOP.id == violation.sop_id).first()
    
    # 2. Build Evidence Chain (Part 3)
    
    # A. Link Active Filter Context
    latest_filter = db.query(FilterAuditLog)\
        .filter(FilterAuditLog.user_id == actor_id)\
        .order_by(desc(FilterAuditLog.created_at))\
        .first()
    
    if latest_filter:
        add_evidence_node(db, violation.id, "FILTER_APPLIED", latest_filter.id)
        
    # B. Add Violation Metadata
    add_evidence_node(db, violation.id, "VIOLATION_DETECTED", violation.id)
    
    # C. Link SOP Invocation
    add_evidence_node(db, violation.id, "SOP_INVOKED", sop.id)

    # 3. Execute Enforcement (Part 2.3)
    actions = db.query(EnforcementAction).filter(EnforcementAction.sop_id == sop.id).all()
    for action in actions:
        event = EnforcementEvent(
            id=uuid.uuid4(),
            violation_id=violation.id,
            sop_id=sop.id,
            action_type=action.action_type,
            executed_at=datetime.now(timezone.utc),
            executed_by="SYSTEM",
            outcome="EXECUTED"
        )
        db.add(event)
        
        # Add enforcement to evidence chain
        add_evidence_node(db, violation.id, "ENFORCEMENT_EXECUTED", event.id)

    db.commit()
