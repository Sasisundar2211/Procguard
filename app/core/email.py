import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging

logger = logging.getLogger(__name__)

def send_email(
    to: list[str],
    subject: str,
    body: str,
    attachments: list[tuple[str, bytes]] = None
):
    """
    Robust Email Dispatcher (Step 5).
    Supports SMTP with TLS. Falls back to logging if not configured.
    """
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        logger.warning(f"SMTP credentials missing. LACKING REAL EMAIL CAPABILITY.")
        logger.info(f"MOCK EMAIL SENT TO {to}: {subject}")
        return True

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachments:
        for filename, content in attachments:
            part = MIMEApplication(content, Name=filename)
            part["Content-Disposition"] = f'attachment; filename="{filename}"'
            msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email successfully sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise RuntimeError(f"Email service unavailable: {str(e)}")
