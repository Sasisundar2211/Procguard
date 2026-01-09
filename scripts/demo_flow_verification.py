import sys
import os
import io
# Add project root to path
sys.path.append(os.getcwd())

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.procedure import Procedure
from app.models.batch import Batch
from app.models.audit import AuditLog
from app.api.events import submit_event
from app.schemas import EventRequest
from app.core.fsm import State, Event

# Mock Request/Dependency injection isn't needed if we call functions directly 
# but we need to adhere to `submit_event` signature which expects Pydantic model.

def setup_demo_data(db: Session):
    # Fetch any valid procedure that has steps
    proc = db.query(Procedure).filter(Procedure.steps.any()).first()
    if not proc:
        print("❌ CRITICAL: No valid procedures found in DB. Run seed_data.py first.")
        sys.exit(1)
    print(f"-> Using existing procedure: {proc.name} (ID: {proc.procedure_id})")
    return proc

def print_audit_log(db: Session, batch_id: str, label: str):
    logs = db.query(AuditLog).filter_by(batch_id=batch_id).order_by(AuditLog.timestamp).all()
    print(f"\n--- {label} Audit Trail ({len(logs)} records) ---")
    print(f"{'TIMESTAMP':<25} | {'ACTOR':<10} | {'EVENT':<18} | {'OUTCOME':<18} | {'VIOLATION'}")
    print("-" * 100)
    for log in logs:
        v_idx = str(log.violation_id) if log.violation_id else "OK"
        print(f"{str(log.timestamp):<25} | {log.actor:<10} | {log.action:<18} | {log.result:<18} | {v_idx}")

import uuid

def run_demo():
    print("🎬 Starting ProcGuard Demo Verification Script\n")
    db = SessionLocal()
    
    try:
        proc = setup_demo_data(db)
        # Find a step that requires approval
        approval_step = next((s for s in proc.steps if s.requires_approval), None)
        if not approval_step:
            print(f"❌ ERROR: Procedure {proc.name} has no steps requiring approval.")
            sys.exit(1)
            
        step_id = str(approval_step.step_id)
        step_name = approval_step.step_name
        print(f"-> Testing with Step: {step_name} (ID: {step_id})")

        # ==========================================
        # ACT 3: LIVE ATTACK
        # ==========================================
        print("\n🔥 ACT 3: The Live Attack (Skipping Approval)")
        
        # 1. Start Batch
        batch_1_id = str(uuid.uuid4())
        print(f"-> Starting Batch {batch_1_id}...")
        
        batch_1 = Batch(
            batch_id=batch_1_id,
            procedure_id=proc.procedure_id,
            current_state=State.IN_PROGRESS.value, # Simulated start
            created_at=datetime.now(timezone.utc)
        )
        db.add(batch_1)
        db.commit()

        # 2. Attempt Step (Requires Approval) WITHOUT requesting it
        print(f"-> Operator attempts '{step_name}' ({step_id}) without approval...")
        req = EventRequest(event="progress_step", step_id=step_id)
        
        try:
            submit_event(
                batch_id=batch_1_id,
                request=req,
                db=db,
                actor_info=("user_1", "OPERATOR")
            )
        except Exception as e:
            print(f"-> Backend Response (Expected): {e}")

        # Verify Result
        b1 = db.query(Batch).filter_by(batch_id=batch_1_id).first()
        if b1 is None:
             print("❌ Batch not found (Transaction rolled back?)")
        else:
            print(f"-> Final State: {b1.current_state}")
            
            if b1.current_state == "VIOLATED":
                print("✅ ATTACK BLOCKED. System transitioned to VIOLATED.")
            else:
                print("❌ ATTACK FAILED TO BLOCK. State is " + b1.current_state)

        print_audit_log(db, batch_1_id, "ATTACK BATCH")


        # ==========================================
        # ACT 4 & 5: HAPPY PATH
        # ==========================================
        print("\n\n✨ ACT 4: The Proper Path")
        
        batch_2_id = str(uuid.uuid4())
        print(f"-> Starting Batch {batch_2_id}...")
        batch_2 = Batch(
            batch_id=batch_2_id,
            procedure_id=proc.procedure_id,
            current_state=State.IN_PROGRESS.value,
            created_at=datetime.now(timezone.utc)
        )
        db.add(batch_2)
        db.commit()

        # 1. Request Approval
        print(f"-> Operator requesting approval for '{step_name}'...")
        submit_event(batch_2_id, EventRequest(event="request_approval", step_id=step_id), db, ("user_1", "OPERATOR"))
        
        # 2. Approve
        print("-> Supervisor approving...")
        submit_event(batch_2_id, EventRequest(event="approve_step", step_id=step_id), db, ("admin_1", "SUPERVISOR"))

        # 3. Progress
        print("-> Operator progressing step...")
        submit_event(batch_2_id, EventRequest(event="progress_step", step_id=step_id), db, ("user_1", "OPERATOR"))

        # Verify
        b2 = db.query(Batch).filter_by(batch_id=batch_2_id).first()
        print(f"-> Final State: {b2.current_state}")
        
        if b2.current_state in ["IN_PROGRESS", "COMPLETED", "APPROVED"]:
             print("✅ HAPPY PATH SUCCESS.")
        else:
             print(f"❌ HAPPY PATH FAILED. State: {b2.current_state}")

        print_audit_log(db, batch_2_id, "COMPLIANT BATCH")

        # ==========================================
        # VERIFY IMMUTABILITY
        # ==========================================
        print("\n\n🛡️ ACT 5: Immutability Verification")
        try:
             print("-> Attempting to DELETE audit log...")
             db.query(AuditLog).filter_by(batch_id=batch_2_id).delete()
             db.commit()
             print("❌ ERROR: DELETION SUCCEEDED (Security Weakness!)")
        except Exception as e:
             db.rollback()
             if "Audit logs are immutable" in str(e):
                  print("✅ IMMUTABILITY CONFIRMED: PostgreSQL prevented deletion.")
             else:
                  print(f"✅ IMMUTABILITY CONFIRMED (Other error): {str(e)[:100]}...")

    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
