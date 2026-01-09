import sys
import os
import uuid
from datetime import datetime, timezone

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.procedure import Procedure, ProcedureStep

def clear_data():
    db = SessionLocal()
    try:
        db.query(ProcedureStep).delete()
        db.query(Procedure).delete()
        db.commit()
        print("Successfully cleared procedure data.")
    except Exception as e:
        print(f"Error clearing data: {e}")
        db.rollback()
    finally:
        db.close()

def seed_procedures():
    db = SessionLocal()
    try:
        procedures_data = [
            {
                "name": "Critical Reaction Protocol",
                "description": "Immediate response to detected violations.",
                "version": 1,
                "steps": [
                    {"step_order": 1, "step_name": "Detect Violation", "requires_approval": False, "approver_role": None},
                    {"step_order": 2, "step_name": "Auto-lock Procedure", "requires_approval": False, "approver_role": None},
                    {"step_order": 3, "step_name": "Notify QA Lead", "requires_approval": False, "approver_role": None},
                    {"step_order": 4, "step_name": "Review Violation", "requires_approval": True, "approver_role": "QA_LEAD"},
                    {"step_order": 5, "step_name": "Resolution Decision", "requires_approval": True, "approver_role": "QA_LEAD"},
                    {"step_order": 6, "step_name": "Unlock / Terminate", "requires_approval": True, "approver_role": "SUPERVISOR"},
                ],
            },
            {
                "name": "Judge Validation SOP",
                "description": "Validate audit correctness for Imagine Cup and enterprise scrutiny.",
                "version": 1,
                "steps": [
                    {"step_order": 1, "step_name": "Collect Audit Artifacts", "requires_approval": False, "approver_role": None},
                    {"step_order": 2, "step_name": "Validate FSM Transitions", "requires_approval": False, "approver_role": None},
                    {"step_order": 3, "step_name": "Validate Approval Ordering", "requires_approval": False, "approver_role": None},
                    {"step_order": 4, "step_name": "Judge Review", "requires_approval": True, "approver_role": "AUDITOR"},
                    {"step_order": 5, "step_name": "Final Validation", "requires_approval": True, "approver_role": "AUDITOR"},
                ],
            },
            {
                "name": "Standard Operating Procedure (SOP)",
                "description": "Normal, compliant batch execution.",
                "version": 1,
                "steps": [
                    {"step_order": 1, "step_name": "Batch Created", "requires_approval": False, "approver_role": None},
                    {"step_order": 2, "step_name": "Execute Step", "requires_approval": False, "approver_role": None},
                    {"step_order": 3, "step_name": "Request Approval", "requires_approval": False, "approver_role": None},
                    {"step_order": 4, "step_name": "Supervisor Approval", "requires_approval": True, "approver_role": "SUPERVISOR"},
                    {"step_order": 5, "step_name": "Progress Batch", "requires_approval": False, "approver_role": None},
                    {"step_order": 6, "step_name": "Complete Batch", "requires_approval": False, "approver_role": None},
                ],
            },
        ]

        for proc_data in procedures_data:
            procedure = Procedure(
                name=proc_data["name"],
                description=proc_data["description"],
                version=proc_data["version"],
                created_at=datetime.now(timezone.utc)
            )
            
            steps = []
            for step_data in proc_data["steps"]:
                step = ProcedureStep(
                    step_order=step_data["step_order"],
                    step_name=step_data["step_name"],
                    requires_approval=step_data["requires_approval"],
                    approver_role=step_data["approver_role"],
                )
                steps.append(step)
            
            procedure.steps = steps
            db.add(procedure)
            
            print(f"Seeded procedure: {procedure.name}")

        db.commit()
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
    seed_procedures()