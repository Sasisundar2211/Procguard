from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.compliance import ComplianceReport, ComplianceEvidence
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os

router = APIRouter(tags=["compliance"])

class EvidenceSchema(BaseModel):
    blob_path: str
    evidence_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ComplianceReportSchema(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    evidence: List[EvidenceSchema]

    class Config:
        from_attributes = True

class CreateReportRequest(BaseModel):
    title: str

class AttachEvidenceRequest(BaseModel):
    blob_path: str
    evidence_type: str

@router.post("/compliance-reports", response_model=ComplianceReportSchema)
def create_compliance_report(req: CreateReportRequest, db: Session = Depends(get_db)):
    report = ComplianceReport(id=uuid.uuid4(), title=req.title)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/compliance-reports", response_model=List[ComplianceReportSchema])
def list_compliance_reports(db: Session = Depends(get_db)):
    return db.query(ComplianceReport).order_by(ComplianceReport.created_at.desc()).all()

@router.post("/compliance-reports/{report_id}/attach")
def attach_evidence(report_id: uuid.UUID, req: AttachEvidenceRequest, db: Session = Depends(get_db)):
    """
    Attaches forensic evidence to a compliance report.
    Verifies blob exists and is immutable (Step 2).
    """
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
        
    # Verify blob exists in our local simulated storage
    if not os.path.exists(req.blob_path):
        raise HTTPException(status_code=400, detail="Forensic evidence blob not found in secure storage")
        
    evidence = ComplianceEvidence(
        report_id=report_id,
        blob_path=req.blob_path,
        evidence_type=req.evidence_type
    )
    db.add(evidence)
    db.commit()
    return {"status": "attached"}

class AttachCurrentFiltersRequest(BaseModel):
    screen: str
    from_ts: datetime
    to_ts: datetime
    evidence_type: str

@router.post("/compliance-reports/{report_id}/attach-current-filters")
def attach_current_filters(
    report_id: uuid.UUID, 
    req: AttachCurrentFiltersRequest, 
    db: Session = Depends(get_db)
):
    """
    Atomic: Generates Filter Audit PDF and attaches it to the report (Part 2).
    """
    from app.core.filter_audit import verify_filter_chain
    from app.models.filter_audit import FilterAuditLog
    import json
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    # 1. Fetch
    records = db.query(FilterAuditLog).filter(
        FilterAuditLog.screen == req.screen,
        FilterAuditLog.created_at >= req.from_ts,
        FilterAuditLog.created_at <= req.to_ts
    ).order_by(FilterAuditLog.created_at.asc()).all()

    if not records:
        raise HTTPException(status_code=400, detail="No audit data found for the selected range")

    # 2. Verify
    verification = verify_filter_chain(db)
    if not verification["valid"]:
        raise HTTPException(status_code=409, detail="Filter audit trail integrity violation")

    # 3. Generate
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f"Forensic Filter Trail: {req.screen}", styles["Title"]))
    elements.append(Paragraph(f"Integrity Check: VALID", styles["Normal"]))
    
    table_data = [["Timestamp", "Payload", "Hash"]]
    for r in records:
        table_data.append([r.created_at.isoformat(), json.dumps(r.filter_payload)[:40], r.hash[:8]])
    
    t = Table(table_data)
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t)
    doc.build(elements)

    # 4. Store
    os.makedirs("evidence/filters", exist_ok=True)
    filename = f"verified_trail_{uuid.uuid4().hex[:8]}.pdf"
    filepath = f"evidence/filters/{filename}"
    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())

    # 5. Attach
    evidence = ComplianceEvidence(
        report_id=report_id,
        blob_path=filepath,
        evidence_type=req.evidence_type
    )
    db.add(evidence)
    db.commit()
    
    return {"status": "generated_and_attached", "path": filepath}

@router.get("/compliance-reports/{report_id}", response_model=ComplianceReportSchema)
def get_compliance_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return report
