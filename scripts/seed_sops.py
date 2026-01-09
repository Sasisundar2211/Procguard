from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.sop import SOP, SOPRule, EnforcementAction
import uuid
from datetime import datetime, timezone
import hashlib

def seed_sops():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(SOP).first():
            print("SOPs already seeded.")
            return

        # 1. Critical Reaction Protocol v1
        sop1 = SOP(
            id=uuid.uuid4(),
            name="Critical Reaction Protocol",
            version=1,
            immutable_hash=hashlib.sha256(b"CRP_V1").hexdigest(),
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        db.add(sop1)
        
        # Map rule
        rule1 = SOPRule(sop_id=sop1.id, rule_code="INVALID_FSM_TRANSITION")
        db.add(rule1)
        
        # Enforcement Action
        action1 = EnforcementAction(
            id=uuid.uuid4(),
            sop_id=sop1.id,
            action_type="LOCK_PROCEDURE",
            parameters={"scope": "BATCH", "unlock_requires": "QA_LEAD"},
            created_at=datetime.now(timezone.utc)
        )
        db.add(action1)

        # 2. Judge Validation SOP v1
        sop2 = SOP(
            id=uuid.uuid4(),
            name="Judge Validation SOP",
            version=1,
            immutable_hash=hashlib.sha256(b"JV_SOP_V1").hexdigest(),
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        db.add(sop2)
        
        # Map rule
        rule2 = SOPRule(sop_id=sop2.id, rule_code="TERMINAL_STATE_MUTATION")
        db.add(rule2)
        
        # Enforcement Action
        action2 = EnforcementAction(
            id=uuid.uuid4(),
            sop_id=sop2.id,
            action_type="FREEZE_BATCH",
            parameters={"scope": "BATCH", "requires_review": True},
            created_at=datetime.now(timezone.utc)
        )
        db.add(action2)

        db.commit()
        print("SOPs and Rules seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sops()
