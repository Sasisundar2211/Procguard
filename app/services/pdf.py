from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_authoritative_timeline_pdf(db, batch_id):
    """
    Authoritative PDF Generator (Step 4).
    Fetches required data and renders the forensic document.
    """
    from app.models.batch import Batch
    from app.models.audit import AuditLog
    
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        return None
        
    logs = db.query(AuditLog).filter(AuditLog.batch_id == batch_id).order_by(AuditLog.timestamp.desc()).all()
    
    # Create a simple container for the renderer that matches expected interface
    class TimelineData:
        batch_id = str(batch.batch_id)
        procedure_id = str(batch.procedure_id)
        procedure_version = batch.procedure_version
        stages = [] # Simplified for the forensic cert
        
    return render_timeline_pdf(TimelineData(), logs)

def render_timeline_pdf(timeline_data, audit_logs):
    """
    Deterministic (Phase 2): Render authoritative PDF artifact.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "PROCGUARD AUTHORITATIVE BATCH TIMELINE")
    
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(40, height - 85, f"Batch ID: {timeline_data.batch_id}")
    c.drawString(40, height - 100, f"Procedure: {timeline_data.procedure_id} (v{timeline_data.procedure_version})")

    # Section 1: Stages
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "Enforcement Stages")
    
    y = height - 150
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "Stage Label")
    c.drawString(200, y, "Expected Window")
    c.drawString(300, y, "Status")
    
    y -= 15
    c.setFont("Helvetica", 9)
    if not timeline_data.stages:
        c.drawString(40, y, "Full stage timeline preserved in digital records.")
        y -= 25
    else:
        for stage in timeline_data.stages:
            c.drawString(40, y, stage.label)
            c.drawString(200, y, f"Day {stage.expected_window[0]} - {stage.expected_window[1]}")
            c.drawString(300, y, getattr(stage, 'status', 'N/A'))
            y -= 12
            if y < 100:
                c.showPage()
                y = height - 50

    # Section 2: Audit Trail
    y -= 20
    if y < 150:
        c.showPage()
        y = height - 50
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Immutable Audit Logs")
    y -= 20
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, y, "Timestamp")
    c.drawString(180, y, "Actor")
    c.drawString(250, y, "Action")
    c.drawString(350, y, "Result")
    c.drawString(420, y, "State Change")
    
    y -= 12
    c.setFont("Helvetica", 8)
    for log in audit_logs:
        log_ts = log.timestamp if hasattr(log, 'timestamp') else getattr(log, 'created_at', None)
        ts_str = log_ts.strftime('%Y-%m-%d %H:%M:%S') if log_ts else "N/A"
        c.drawString(40, y, ts_str)
        c.drawString(180, y, str(log.actor or "SYSTEM")[:15])
        c.drawString(250, y, str(log.action)[:20])
        c.drawString(350, y, str(log.result))
        
        state_info = "—"
        if hasattr(log, 'expected_state') and log.expected_state and log.actual_state:
            state_info = f"{log.expected_state} -> {log.actual_state}"
        c.drawString(420, y, state_info)
        
        y -= 10
        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()

    return buffer.getvalue()

def render_violation_chain_pdf(violation, opa_log=None, audit_log=None):
    """
    Forensic Verification PDF (Step 5).
    Embeds the cryptographic chain of custody hashes directly in the document.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 60, "FORENSIC VIOLATION RECORD")
    
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 80, f"Violation ID: {violation.id}")
    c.drawString(40, height - 95, f"Rule Violated: {violation.rule}")
    c.drawString(40, height - 110, f"Detected At: {violation.detected_at.isoformat()}")
    c.drawString(40, height - 125, f"Batch ID: {violation.batch_id}")

    # Body
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 160, "Event Context")
    c.setFont("Helvetica", 11)
    y = height - 180
    c.drawString(40, y, f"This breach was detected during an automated FSM transition check.")
    y -= 15
    c.drawString(40, y, f"The system enforced the following SOP: {violation.sop.name if violation.sop else 'None'}")

    # Section: Evidence Verification Block (Step 5)
    y = 200
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(40, y + 20, width - 40, y + 20)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "EVIDENCE VERIFICATION BLOCK (SHA-256)")
    c.setFont("Courier-Bold", 9)
    y -= 25
    c.drawString(40, y, f"OPA Decision Hash:    {violation.opa_decision_hash or 'N/A'}")
    y -= 15
    c.drawString(40, y, f"Violation Hash:       {violation.violation_hash or 'N/A'}")
    y -= 15
    c.drawString(40, y, f"Audit Entry Hash:     {audit_log.audit_hash if audit_log else 'N/A'}")
    
    y -= 25
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "GENERATED AT:")
    c.setFont("Helvetica", 9)
    c.drawString(130, y, f"{datetime.utcnow().isoformat()}Z")
    
    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "SYSTEM:")
    c.setFont("Helvetica", 9)
    c.drawString(130, y, "ProcGuard v1.0 (Enterprise Forensic Edition)")

    c.showPage()
    c.save()

    return buffer.getvalue()
