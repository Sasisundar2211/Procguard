import hashlib
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.filter_audit import FilterAuditLog

def normalize_payload(payload: dict) -> str:
    """Deterministic JSON serialization."""
    return json.dumps(payload, sort_keys=True)

def normalize_timestamp(dt: datetime) -> str:
    """Forensic timestamp normalization (ISO 8601 UTC with 'Z')."""
    # Ensure it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # Format to a fixed precision to avoid microsecond round-trip issues
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def compute_filter_hash(prev_hash: str, payload: dict, user_id: str, screen: str, dt: datetime) -> str:
    """
    Computes a SHA-256 hash for a filter event, chained to the previous record.
    hash = SHA256(prev_hash + user_id + screen + filter_payload + created_at)
    """
    payload_json = normalize_payload(payload)
    ts_str = normalize_timestamp(dt)
    
    raw = f"{prev_hash or ''}{user_id}{screen}{payload_json}{ts_str}"
    return hashlib.sha256(raw.encode()).hexdigest()

def log_filter_event(
    db: Session,
    user_id: str,
    screen: str,
    filter_payload: dict
) -> FilterAuditLog:
    """
    Writes a tamper-evident filter audit event to the ledger.
    """
    # 1. Fetch previous record for chaining (ordering by ID or created_at)
    last_log = db.query(FilterAuditLog).order_by(desc(FilterAuditLog.created_at)).first()
    prev_hash = last_log.hash if last_log else None
    
    now = datetime.now(timezone.utc)
    
    # 2. Compute hash
    current_hash = compute_filter_hash(
        prev_hash, 
        filter_payload, 
        user_id, 
        screen, 
        now
    )
    
    # 3. Save to DB
    new_log = FilterAuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        screen=screen,
        filter_payload=filter_payload,
        created_at=now,
        prev_hash=prev_hash,
        hash=current_hash
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def verify_filter_chain(db: Session) -> dict:
    """
    Recomputes the entire hash chain to verify integrity.
    """
    records = db.query(FilterAuditLog).order_by(FilterAuditLog.created_at.asc()).all()
    
    current_prev_hash = None
    checked_count = 0
    
    for record in records:
        expected_hash = compute_filter_hash(
            current_prev_hash,
            record.filter_payload,
            record.user_id,
            record.screen,
            record.created_at
        )
        
        if expected_hash != record.hash:
            return {
                "valid": False,
                "error": f"Chain broken at record {record.id}",
                "checked_records": checked_count,
                "debug": {
                    "recorded_hash": record.hash,
                    "expected_hash": expected_hash,
                    "prev_hash_used": current_prev_hash
                }
            }
        
        current_prev_hash = record.hash
        checked_count += 1
        
    return {
        "valid": True,
        "checked_records": checked_count
    }
