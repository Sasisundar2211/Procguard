from fastapi import APIRouter, Query, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
import uuid

from app.api.deps import get_db, get_current_actor
from app.models.audit import AuditLog
from app.core.filter_audit import log_filter_event, verify_filter_chain
from app.services.audit_service import generate_filter_audit_report
from app.core.circuit_breaker import circuit_breaker

# Removed prefix to allow explicit paths matching frontend
router = APIRouter(tags=["Regulatory Audit"])

class AuditLogSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime
    source: str
    project_id: uuid.UUID
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    client_id: str
    payload: dict
    actor: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    items: List[AuditLogSchema]
    total: int

@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    db: Session = Depends(get_db),
    domain: str = Query("SYSTEM"),
    project_id: Optional[uuid.UUID] = Query(None),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...)
):
    """
    Authoritative Forensic Audit Log Retrieval.
    """
    endpoint = "/audit-logs"
    if circuit_breaker.is_degraded(endpoint):
        return {"items": [], "total": 0}

    try:
        start_time = from_ts.replace(tzinfo=timezone.utc) if from_ts.tzinfo is None else from_ts
        end_time = to_ts.replace(tzinfo=timezone.utc) if to_ts.tzinfo is None else to_ts

        query = db.query(AuditLog).filter(AuditLog.source == domain.upper())
        if project_id:
            query = query.filter(AuditLog.project_id == project_id)
        
        query = query.filter(AuditLog.created_at >= start_time)
        query = query.filter(AuditLog.created_at <= end_time)

        logs = query.order_by(AuditLog.created_at.desc()).all()
        circuit_breaker.record_success(endpoint)
        return {"items": logs, "total": len(logs)}
    except Exception as e:
        circuit_breaker.record_failure(endpoint, type(e).__name__)
        raise HTTPException(status_code=500, detail="Audit query failure")

class FilterEventRequest(BaseModel):
    screen: str
    filter_payload: dict

@router.post("/audit/filter-events")
def create_filter_event(
    req: FilterEventRequest,
    db: Session = Depends(get_db),
    actor_info: tuple[str, str] = Depends(get_current_actor)
):
    actor_id, _ = actor_info
    log = log_filter_event(db, actor_id, req.screen, req.filter_payload)
    return {"status": "ok", "id": str(log.id)}

@router.get("/audit/filter-events/verify")
def verify_filter_logs(db: Session = Depends(get_db)):
    result = verify_filter_chain(db)
    if not result["valid"]:
        raise HTTPException(status_code=409, detail=result)
    return result

@router.get("/audit/filter-events/export")
def export_filter_audit_logs(
    screen: str = Query(...),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    violation_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Exports a tamper-evident Filter Audit Trail as PDF.
    Verifies hash chain integrity BEFORE export.
    """
    pdf_content, error_or_url = generate_filter_audit_report(db, screen, from_ts, to_ts, violation_id)
    
    if not pdf_content:
        raise HTTPException(status_code=400, detail=error_or_url)

    filename = f"filter_audit_{screen}.pdf"
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Forensic-Source": "ProcGuard-Vault",
            "X-Permanent-URL": error_or_url  # blob_url
        }
    )
