from fastapi import APIRouter, Query, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from datetime import datetime, timezone
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
import json
import uuid

from app.api.deps import get_db, get_current_actor
from app.models.audit import AuditLog
from app.models.filter_audit import FilterAuditLog
from app.core.filter_audit import log_filter_event, verify_filter_chain

router = APIRouter()

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
    expected_state: Optional[str] = None
    actual_state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    items: List[AuditLogSchema]
    total: int

from app.core.circuit_breaker import circuit_breaker

@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    db: Session = Depends(get_db),
    domain: str = Query("SYSTEM"),
    project_id: Optional[uuid.UUID] = Query(None),
    event_type: str = Query(None),
    user_id: str = Query(None),
    client_id: str = Query(None),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...)
):
    """
    Hardened Forensic Audit Log Retrieval (Step 3).
    Ensures domain is normalized and all time queries are UTC.
    """
    import logging
    logger = logging.getLogger(__name__)
    endpoint = "/audit-logs"

    # Enterprise Resilience: Check Circuit State
    if circuit_breaker.is_degraded(endpoint):
        logger.warning(f"Circuit OPEN for {endpoint}. Returning degraded (empty) response.")
        return {
            "items": [],
            "total": 0
        }

    try:
        domain_upper = domain.upper()
        
        # Ensure TZ awareness (Forensic Hardening)
        start_time = from_ts.replace(tzinfo=timezone.utc) if from_ts.tzinfo is None else from_ts
        end_time = to_ts.replace(tzinfo=timezone.utc) if to_ts.tzinfo is None else to_ts

        query = db.query(AuditLog)

        # 1. Domain filter (authoritative source)
        query = query.filter(AuditLog.source == domain_upper)
        
        # 2. Forensic filters
        if project_id:
            query = query.filter(AuditLog.project_id == project_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if client_id:
            query = query.filter(AuditLog.client_id == client_id)
        
        # 3. Time scale
        query = query.filter(AuditLog.created_at >= start_time)
        query = query.filter(AuditLog.created_at <= end_time)

        # Sort by creation time (forensic sequence)
        logs = query.order_by(AuditLog.created_at.desc()).all()
        
        circuit_breaker.record_success(endpoint)
        return {
            "items": logs,
            "total": len(logs)
        }
    except Exception as e:
        logger.exception("Audit log fetch failed")
        circuit_breaker.record_failure(endpoint, type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail="Audit log query failed"
        )

@router.get("/audit-logs/export")
def export_audit_logs(
    db: Session = Depends(get_db),
    domain: str = Query("SYSTEM"),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...)
):
    """
    Export raw audit records for external legal review.
    """
    data = get_audit_logs(db, domain=domain, from_ts=from_ts, to_ts=to_ts)
    return Response(
        content=json.dumps(data, indent=4, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=audit_export_{domain}.json"}
    )

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
    Verifies hash chain integrity BEFORE export (Step 2).
    """
    # 1. Fetch records
    records = db.query(FilterAuditLog).filter(
        FilterAuditLog.screen == screen,
        FilterAuditLog.created_at >= from_ts,
        FilterAuditLog.created_at <= to_ts
    ).order_by(FilterAuditLog.created_at.asc()).all()

    if not records:
        raise HTTPException(status_code=204, detail="No data found for selected window")

    # 2. Verify Integrity First (MANDATORY)
    verification = verify_filter_chain(db) # Verifies entire chain up to current
    if not verification["valid"]:
        raise HTTPException(status_code=409, detail="Filter audit trail integrity violation")

    # 3. Generate PDF (Step 4)
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    import os
    import hashlib

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph(f"ProcGuard Filter Audit Trail: {screen}", styles["Title"]))
    elements.append(Paragraph(f"Environment: Production / Courtroom-Safe", styles["Normal"]))
    elements.append(Paragraph(f"Export Timestamp (UTC): {datetime.utcnow().isoformat()}Z", styles["Normal"]))
    elements.append(Paragraph(f"Hash Chain Verified: YES ({verification['checked_records']} records checked)", styles["Normal"]))
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Table
    table_data = [["Timestamp", "User", "Action", "Payload", "Hash (Short)"]]
    for r in records:
        table_data.append([
            r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            r.user_id,
            r.screen,
            json.dumps(r.filter_payload)[:30] + "...",
            r.hash[:12] + "..."
        ])

    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)

    doc.build(elements)
    
    # 4. Store as Evidence (Step 5)
    os.makedirs("evidence/filters", exist_ok=True)
    filename = f"filter_audit_{datetime.utcnow().strftime('%Y%m%dT%H%MZ')}.pdf"
    filepath = f"evidence/filters/{filename}"
    
    pdf_content = buffer.getvalue()
    with open(filepath, "wb") as f:
        f.write(pdf_content)

    # 5. Build Evidence Chain (Part 3)
    if violation_id:
        from app.core.evidence import add_evidence_node
        # Use the hash of the export file as the digital fingerprint
        export_hash = hashlib.sha256(pdf_content).hexdigest()
        add_evidence_node(db, violation_id, "EXPORT_GENERATED", uuid.UUID(int=int(export_hash[:32], 16))) # Simulated UUID from hash

    # Return PDF for download
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
