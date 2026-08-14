"""Email integration.

Sends real email over SMTP (Gmail + app password) when smtp_user/smtp_password
are configured. Otherwise falls back to logging the outbound email to
logs/emails.log, so the rest of the pipeline still runs without credentials.
Every caller only depends on `send_email`'s signature and return shape.
"""

import json
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from app.config import settings

LOG_FILE = settings.logs_dir / "emails.log"


def send_email(to: str, subject: str, body: str) -> dict:
    if settings.smtp_enabled:
        return _send_smtp(to, subject, body)
    return _send_mock(to, subject, body)


def _send_smtp(to: str, subject: str, body: str) -> dict:
    message = EmailMessage()
    message["From"] = f"{settings.email_from_name} <{settings.smtp_user}>"
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "to": to,
        "subject": subject,
        "body": body,
        "provider": "smtp",
    }

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        record["status"] = "sent"
    except (smtplib.SMTPException, OSError) as e:
        record["status"] = "failed"
        record["error"] = str(e)

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def _send_mock(to: str, subject: str, body: str) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "to": to,
        "subject": subject,
        "body": body,
        "provider": "mock",
        "status": "sent",
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record
