"""Simulated email integration.

For the demo this just logs the outbound email to logs/emails.log instead of
calling a real provider, so the whole pipeline can be exercised without Gmail
credentials.

To wire up real Gmail sending later: implement this same `send_email` signature
using the Gmail API (google-api-python-client) with an OAuth2 service account
or user credentials, and nothing else in the codebase needs to change — every
caller only depends on this function's signature and return shape.
"""

import json
from datetime import datetime, timezone

from app.config import settings

LOG_FILE = settings.logs_dir / "emails.log"


def send_email(to: str, subject: str, body: str) -> dict:
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
