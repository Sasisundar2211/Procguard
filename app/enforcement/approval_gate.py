from sqlalchemy.orm import Session
from app.models.approval import Approval

def get_latest_approval(db: Session, batch_id: str) -> Approval:
    return db.query(Approval).filter(
        Approval.batch_id == batch_id
    ).order_by(Approval.created_at.desc()).first()

def can_batch_progress(db: Session, batch_id: str) -> bool:
    """
    Hard enforcement: Nothing progresses without explicit approval.
    """
    approval = get_latest_approval(db, batch_id)

    if not approval:
        return False

    return approval.decision == "APPROVED"
