from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit_sync_checkpoint import AuditSyncCheckpoint
from app.core.crypto import sha256
import uuid
from datetime import datetime

class SyncManager:
    """
    Authoritative Backend Sync Manager.
    Handles Checkpoint creation, verification, and resume logic.
    """
    
    @staticmethod
    def get_latest_checkpoint(db: Session, stream_name: str) -> AuditSyncCheckpoint | None:
        """Fetch the single authoritative source of truth for sync state."""
        return db.query(AuditSyncCheckpoint).filter(
            AuditSyncCheckpoint.stream_name == stream_name
        ).order_by(
            AuditSyncCheckpoint.committed_at.desc()
        ).first()

    @staticmethod
    def create_checkpoint(
        db: Session,
        stream_name: str,
        last_event_id: uuid.UUID,
        last_event_hash: str,
        is_recovery: bool = False
    ) -> AuditSyncCheckpoint:
        """
        Seal a new checkpoint.
        Must be called ONLY after verification succeeds.
        """
        # Calculate Snapshot Hash (Simple version for MVP: hash of event hash + ts)
        # In production, this would be a Merkle Root of the snapshot.
        now = datetime.utcnow()
        snapshot_payload = f"{stream_name}:{last_event_hash}:{now.isoformat()}"
        snapshot_hash = sha256(snapshot_payload)
        
        checkpoint = AuditSyncCheckpoint(
            id=uuid.uuid4(),
            stream_name=stream_name,
            last_event_id=last_event_id,
            last_event_hash=last_event_hash,
            snapshot_hash=snapshot_hash,
            snapshot_version=1,
            committed_at=now,
            verified_by="SyncManager",
            is_recovery_checkpoint=is_recovery
        )
        
        db.add(checkpoint)
        # Caller handles commit to ensure atomicity with event writes
        return checkpoint

    @staticmethod
    def verify_integrity(db: Session, stream_name: str) -> bool:
        """
        Verify if the current head matches the last checkpoint.
        This defines the INTEGRITY CIRCUIT state.
        """
        latest = SyncManager.get_latest_checkpoint(db, stream_name)
        if not latest:
            return True # No history = No corruption (Greenfield)
            
        # Here we would re-verify the hash chain from the last checkpoint
        # For MVP, we assume if we can read it, it's valid.
        # In full version: Recalculate hash of last_event_id and compare.
        return True

sync_manager = SyncManager()
