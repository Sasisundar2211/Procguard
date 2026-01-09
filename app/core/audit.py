import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit import AuditLog

def write_audit_log(
    db: Session,
    action: str,
    batch_id: uuid.UUID = None,
    result: str = "SUCCESS",
    actor: str = "SYSTEM",
    metadata: dict = None,
    expected_state: str = None,
    actual_state: str = None
):
    metadata = metadata or {}
    from app.core.crypto import canonical_hash
    
    payload = {
        "action": action,
        "result": result,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **metadata
    }
    a_hash = canonical_hash(payload)

    # 4. Create AuditLog entry
    audit_log = AuditLog(
        id=uuid.uuid4(),
        batch_id=batch_id,
        actor=actor,
        action=action,
        result=result,
        expected_state=expected_state,
        actual_state=actual_state,
        timestamp=datetime.now(timezone.utc),
        payload=payload,
        source="SYSTEM",
        project_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        client_id="API",
        created_at=datetime.now(timezone.utc),
        audit_hash=a_hash
    )
    db.add(audit_log)
    db.commit()
    return audit_log
