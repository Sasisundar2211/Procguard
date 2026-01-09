from app.core.database import SessionLocal
from app.models.opa_audit import OPAAuditLog
import uuid
from datetime import datetime, timezone, timedelta
import hashlib

def seed_opa_logs():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(OPAAuditLog).first():
            print("OPA logs already seeded.")
            return

        project_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        now = datetime.now(timezone.utc)

        # 1. Denied State Mutation
        log1 = OPAAuditLog(
            id=uuid.uuid4(),
            timestamp=now - timedelta(minutes=10),
            project_id=project_id,
            policy_package="procguard.lifecycle",
            rule="terminal_state_mutation_lock",
            decision="deny",
            resource_type="batch",
            resource_id="BATCH-001",
            input_hash=hashlib.sha256(b"input1").hexdigest(),
            result_hash=hashlib.sha256(b"result1").hexdigest(),
            immutable=True
        )
        db.add(log1)

        # 2. Allowed SOP Invocation
        log2 = OPAAuditLog(
            id=uuid.uuid4(),
            timestamp=now - timedelta(minutes=5),
            project_id=project_id,
            policy_package="procguard.enforcement",
            rule="sop_selection_logic",
            decision="allow",
            resource_type="violation",
            resource_id="VIOL-ABC",
            input_hash=hashlib.sha256(b"input2").hexdigest(),
            result_hash=hashlib.sha256(b"result2").hexdigest(),
            immutable=True
        )
        db.add(log2)

        # 3. Denied Unauthorized Step
        log3 = OPAAuditLog(
            id=uuid.uuid4(),
            timestamp=now - timedelta(minutes=2),
            project_id=project_id,
            policy_package="procguard.rbac",
            rule="operator_can_advance",
            decision="deny",
            resource_type="batch",
            resource_id="BATCH-002",
            input_hash=hashlib.sha256(b"input3").hexdigest(),
            result_hash=hashlib.sha256(b"result3").hexdigest(),
            immutable=True
        )
        db.add(log3)

        db.commit()
        print("OPA Audit Logs seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_opa_logs()
