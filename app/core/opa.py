from sqlalchemy.orm import Session
from app.models.opa_audit import OPAAuditLog
from app.core.crypto import canonical_hash
from datetime import datetime, timezone
import uuid

def record_opa_decision(
    db: Session,
    policy_package: str,
    rule: str,
    decision: str,
    resource_type: str,
    resource_id: str,
    input_facts: dict,
    project_id: uuid.UUID
) -> OPAAuditLog:
    """
    Records an authoritative OPA decision with cryptographic proof (Step 2).
    """
    timestamp = datetime.now(timezone.utc)
    
    # Canonicalize payload for hashing
    payload = {
        "policy_package": policy_package,
        "rule": rule,
        "decision": decision,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "input": input_facts,
        "timestamp": timestamp.isoformat()
    }
    
    import hashlib
    input_hash = canonical_hash(input_facts)
    result_hash = hashlib.sha256(decision.encode("utf-8")).hexdigest()
    
    # Authoritative Hashing (Step 4.1): policy_id + input_hash + result_hash + timestamp
    raw_decision_data = f"{policy_package}:{input_hash}:{result_hash}:{timestamp.isoformat()}"
    decision_hash = hashlib.sha256(raw_decision_data.encode("utf-8")).hexdigest()
    
    opa_log = OPAAuditLog(
        id=uuid.uuid4(),
        timestamp=timestamp,
        project_id=project_id,
        policy_package=policy_package,
        rule=rule,
        decision=decision,
        resource_type=resource_type,
        resource_id=resource_id,
        input_hash=input_hash,
        result_hash=result_hash,
        decision_hash=decision_hash,
        payload=payload,
        immutable=True
    )
    
    db.add(opa_log)
    db.flush() # Ensure ID and data are in session
    return opa_log
