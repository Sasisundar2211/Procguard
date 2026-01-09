from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, REQUIRE_AUDITOR
from app.models.audit import AuditLog
from app.schemas_audit import AuditLogResponse

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
def list_audit_logs(
    source: Optional[str] = Query(None, description="SYSTEM or OPA"),
    project_id: Optional[str] = Query(None, alias="project_id"),
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None, alias="from"),
    until: Optional[datetime] = Query(None, alias="to"),
    q: Optional[str] = Query(None, description="Search in payload"),
    force: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)

    # Deterministic SQL Filtering (Step 3)
    if source:
        query = query.filter(AuditLog.source == source)
    if project_id:
        query = query.filter(AuditLog.project_id == project_id)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if client_id:
        query = query.filter(AuditLog.client_id == client_id)
    
    if since:
        query = query.filter(AuditLog.created_at >= since)
    if until:
        query = query.filter(AuditLog.created_at <= until)

    if q:
        # Search in payload JSONB stringified (Step 7)
        # Using cast to text for ILIKE search in JSONB
        query = query.filter(AuditLog.payload.cast(text("text")).ilike(f"%{q}%"))

    # Force bypass cache logic could be added here if we had Redis
    # if force: 
    #     db.expire_all()

    return query.order_by(AuditLog.created_at.desc()).all()

@router.get("/export")
def export_audit_logs(
    source: Optional[str] = None,
    project_id: Optional[str] = None,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    client_id: Optional[str] = None,
    since: Optional[datetime] = Query(None, alias="from"),
    until: Optional[datetime] = Query(None, alias="to"),
    q: Optional[str] = None,
    format: str = "json",
    db: Session = Depends(get_db)
):
    # Identical filters to list_audit_logs (Step 10)
    # Reusing logic for audit safety
    logs = list_audit_logs(source, project_id, event_type, user_id, client_id, since, until, q, False, db)
    
    # In a real app we'd convert to CSV if requested
    return logs
