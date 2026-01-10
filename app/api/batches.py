from typing import List, Optional, Dict
from uuid import UUID

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_actor
from app.schemas import BatchCreateRequest, BatchResponse
from app.models.batch import Batch
from app.core.fsm import Event, State
from app.core.transitions import execute_transition
from app.core.audit import write_audit_log

router = APIRouter()

@router.get("/", response_model=List[BatchResponse])
def list_batches(
    skip: int = 0,
    limit: int = 100,
    recent: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(Batch)
    if recent:
        query = query.order_by(Batch.created_at.desc())
    batches = query.offset(skip).limit(limit).all()
    return batches

@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    request: BatchCreateRequest,
    db: Session = Depends(get_db),
    actor_info: tuple[str, str] = Depends(get_current_actor),
):
    actor_id, actor_role = actor_info
    
    # Check if batch already exists
    existing_batch = db.query(Batch).filter(Batch.batch_id == request.batch_id).first()
    if existing_batch:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Batch already exists"
        )

    new_batch = Batch(
        batch_id=request.batch_id,
        procedure_id=request.procedure_id,
        procedure_version=request.procedure_version,
        current_state=State.CREATED.value,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_batch)
    
    try:
        db.flush() # Verify constraints but allow rollback
        
        execute_transition(
            db=db,
            batch=new_batch,
            event=Event.START_BATCH,
            actor=actor_id,
            actor_role=actor_role,
            occurred_at=datetime.now(timezone.utc),
            procedure_version=request.procedure_version 
        )
        return new_batch
    except PermissionError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
):
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: List[str]
    subject: str
    message: Optional[str] = None
    attachments: Dict[str, bool]

@router.post("/{batch_id}/email")
def email_batch_report(
    batch_id: UUID, 
    payload: EmailRequest,
    db: Session = Depends(get_db),
    actor_info: tuple[str, str] = Depends(get_current_actor)
):
    """
    Forensic Email Dispatch (Step 3/4).
    Generates artifacts and sends via SMTP with authoritative audit logging.
    """
    from app.core.email import send_email
    from app.services.pdf import generate_authoritative_timeline_pdf
    
    actor_id, _ = actor_info
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch artifact not found")

    # 1. Generate Attachments
    email_attachments = []
    if payload.attachments.get("timeline_pdf"):
        pdf_bytes = generate_authoritative_timeline_pdf(db, batch_id)
        if pdf_bytes:
            email_attachments.append((f"batch_{batch_id}_timeline.pdf", pdf_bytes))

    # 2. Send Email
    try:
        send_email(
            to=payload.to,
            subject=payload.subject,
            body=payload.message or "",
            attachments=email_attachments
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Email delivery failed: {str(e)}")

    # 3. Authoritative Audit (Step 7)
    write_audit_log(
        db=db,
        action="EMAIL_SENT",
        batch_id=batch_id,
        actor=actor_id,
        metadata={
            "recipients": payload.to,
            "subject": payload.subject,
            "attachment_types": [k for k, v in payload.attachments.items() if v]
        }
    )

    return {"status": "sent", "recipients": payload.to}
