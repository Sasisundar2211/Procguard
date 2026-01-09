import hashlib
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.sop import EvidenceChain

def compute_evidence_hash(event_type: str, source_id: uuid.UUID, previous_hash: str, created_at: datetime) -> str:
    """
    Forensic Hashing Rule (MANDATORY):
    hash = sha256(event_type + source_id + previous_hash + created_at)
    """
    ts_str = created_at.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    raw = f"{event_type}{str(source_id)}{previous_hash or ''}{ts_str}"
    return hashlib.sha256(raw.encode()).hexdigest()

def add_evidence_node(
    db: Session,
    violation_id: uuid.UUID,
    event_type: str,
    source_id: uuid.UUID
) -> EvidenceChain:
    """
    Appends a new verified node to the evidence chain for a specific violation.
    """
    # 1. Fetch previous node for this violation
    last_node = db.query(EvidenceChain)\
        .filter(EvidenceChain.violation_id == violation_id)\
        .order_by(desc(EvidenceChain.created_at))\
        .first()
        
    prev_hash = last_node.hash if last_node else None
    now = datetime.now(timezone.utc)
    
    # 2. Compute hash
    current_hash = compute_evidence_hash(event_type, source_id, prev_hash, now)
    
    # 3. Persist
    new_node = EvidenceChain(
        id=uuid.uuid4(),
        violation_id=violation_id,
        event_type=event_type,
        source_id=source_id,
        hash=current_hash,
        previous_hash=prev_hash,
        created_at=now
    )
    
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node

def verify_evidence_chain(db: Session, violation_id: uuid.UUID) -> dict:
    """
    Recomputes the entire evidence chain for a violation to ensure forensic integrity.
    """
    nodes = db.query(EvidenceChain)\
        .filter(EvidenceChain.violation_id == violation_id)\
        .order_by(EvidenceChain.created_at.asc())\
        .all()
        
    current_prev_hash = None
    checked_count = 0
    
    for node in nodes:
        expected_hash = compute_evidence_hash(
            node.event_type,
            node.source_id,
            current_prev_hash,
            node.created_at
        )
        
        if expected_hash != node.hash:
            return {
                "valid": False,
                "error": f"Integrity Breach at node {node.id}",
                "checked_nodes": checked_count
            }
            
        current_prev_hash = node.hash
        checked_count += 1
        
    return {
        "valid": True,
        "checked_nodes": checked_count
    }
