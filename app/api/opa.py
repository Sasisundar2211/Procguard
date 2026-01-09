from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.api.deps import get_db
from app.models.opa_audit import OPAAuditLog

router = APIRouter()

class OPAAuditLogSchema(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    project_id: uuid.UUID
    policy_package: str
    rule: str
    decision: str
    resource_type: str
    resource_id: Optional[str] = None
    input_hash: str
    result_hash: str
    linked_violation_id: Optional[uuid.UUID] = None
    immutable: bool

    model_config = ConfigDict(from_attributes=True)

class OPAAuditLogListResponse(BaseModel):
    items: List[OPAAuditLogSchema]
    total: int

@router.get("/audit-logs", response_model=OPAAuditLogListResponse)
def get_opa_audit_logs(
    db: Session = Depends(get_db),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    project_id: Optional[uuid.UUID] = Query(None),
    decision: Optional[str] = Query(None) # allow | deny
):
    """
    Authoritative OPA Policy Decision Audit Trail (Step 2).
    Exposes every policy decision influencing enforcement.
    """
    try:
        # Ensure TZ awareness
        start_time = from_ts.replace(tzinfo=timezone.utc) if from_ts.tzinfo is None else from_ts
        end_time = to_ts.replace(tzinfo=timezone.utc) if to_ts.tzinfo is None else to_ts

        query = db.query(OPAAuditLog)
        
        # Filters
        if project_id:
            query = query.filter(OPAAuditLog.project_id == project_id)
        if decision:
            query = query.filter(OPAAuditLog.decision == decision)
            
        query = query.filter(OPAAuditLog.timestamp >= start_time)
        query = query.filter(OPAAuditLog.timestamp <= end_time)

        logs = query.order_by(OPAAuditLog.timestamp.desc()).all()
        
        return {
            "items": logs,
            "total": len(logs)
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("OPA Audit log fetch failed")
        raise HTTPException(
            status_code=500,
            detail="OPA Audit log query failed"
        )

@router.get("/audit-logs/export")
def export_opa_audit_logs(
    db: Session = Depends(get_db),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    project_id: Optional[uuid.UUID] = Query(None)
):
    """
    Export raw OPA audit records for external legal review.
    """
    import json
    from fastapi import Response
    
    data = get_opa_audit_logs(db, from_ts=from_ts, to_ts=to_ts, project_id=project_id)
    return Response(
        content=json.dumps(data, indent=4, default=str),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=opa_audit_export.json"}
    )
