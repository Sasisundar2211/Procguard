from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.batch import Batch
from app.core.fsm import Event, State
from app.core.transitions import execute_transition
import uuid
from datetime import datetime, timezone
import os

def simulate_violation():
    db = SessionLocal()
    try:
        # Create a batch
        batch_id = uuid.uuid4()
        batch = Batch(
            batch_id=batch_id,
            procedure_id=uuid.UUID("057d5215-7207-4aa5-8261-a5038a9a6746"),
            procedure_version=1,
            current_state=State.IN_PROGRESS.value,
            created_at=datetime.now(timezone.utc)
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        print(f"Created batch {batch.batch_id}")

        # Simulate INVALID_FSM_TRANSITION
        # Requesting approval from IN_PROGRESS is valid, but let's try something else.
        # Actually, let's just use an event that isn't allowed from IN_PROGRESS.
        # ALLOWED from IN_PROGRESS: PROGRESS_STEP, REQUEST_APPROVAL, CANCEL, PAUSE
        # Let's try APPROVE_STEP (usually requires AWAITING_APPROVAL)
        
        try:
            execute_transition(
                db=db,
                batch=batch,
                event=Event.APPROVE_STEP,
                actor="test_user",
                actor_role="SUPERVISOR",
                occurred_at=datetime.now(timezone.utc)
            )
        except RuntimeError as e:
            print(f"Caught expected violation: {e}")
            
        # Refetch batch to check state
        db.refresh(batch)
        print(f"Batch state: {batch.current_state}")
        
        # Check if violation was created
        from app.models.violation import Violation
        violation = db.query(Violation).filter(Violation.batch_id == batch.batch_id).first()
        if violation:
            print(f"Violation created: {violation.id} with rule {violation.rule}")
            print(f"SOP linked: {violation.sop_id}")
            
            # Check evidence chain
            from app.models.sop import EvidenceChain
            nodes = db.query(EvidenceChain).filter(EvidenceChain.violation_id == violation.id).all()
            print(f"Evidence chain length: {len(nodes)}")
            for node in nodes:
                print(f" - {node.event_type} (Hash: {node.hash[:8]}...)")

    finally:
        db.close()

if __name__ == "__main__":
    simulate_violation()
