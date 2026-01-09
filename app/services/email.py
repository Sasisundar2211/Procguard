import smtplib
from email.message import EmailMessage
import os

def send_email(to: str, subject: str, body: str):
    """
    Phase 3: Controlled Email Delivery.
    (Mock implementation using localhost or simple logging if SMTP fails)
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "procguard@authoritative.system"
    msg["To"] = to
    msg.set_content(body)

    # In a production environment, we'd use a real SMTP server or Azure Communication Services
    # For MVP verification, we attempt localhost and fallback to logging.
    try:
        smtp_host = os.getenv("SMTP_HOST", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", 25))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"SMTP Delivery skipped/failed (Safe for demo): {str(e)}")
        print(f"--- MOCK EMAIL START ---")
        print(f"TO: {to}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{body}")
        print(f"--- MOCK EMAIL END ---")

def render_timeline_email(timeline_data):
    """
    Render a clean text body for the timeline email.
    """
    lines = [
        "PROCGUARD AUTHORITATIVE AUDIT ARTIFACT",
        "=" * 40,
        f"Batch ID: {timeline_data.batch_id}",
        f"Procedure: {timeline_data.procedure_id} (v{timeline_data.procedure_version})",
        f"Generated: {os.uname().nodename} at {os.popen('date').read().strip()}",
        "",
        "ENFORCEMENT STATES",
        "-" * 20,
    ]
    
    for stage in timeline_data.stages:
        lines.append(f"[{stage.status:^12}] {stage.label}")
        
    lines.append("")
    lines.append("This is an automated forensic artifact from ProcGuard.")
    lines.append("Verify this document integrity at the Secure Auditor Portal.")
    
    return "\n".join(lines)
