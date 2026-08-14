"""Simulated Slack integration — logs to logs/slack.log instead of calling a
real webhook. Swap in a POST to a Slack Incoming Webhook URL later; the
`notify` signature and return shape stay the same for every caller.
"""

import json
from datetime import datetime, timezone

from app.config import settings

LOG_FILE = settings.logs_dir / "slack.log"


def notify_high_value_lead(company: str | None, name: str, budget: float | None, need: str, score: int) -> dict:
    text = (
        f"🔥 HIGH VALUE LEAD\n\n"
        f"Company: {company or 'n/a'}\n"
        f"Contact: {name}\n"
        f"Budget: {f'€{budget:,.0f}' if budget else 'n/a'}\n"
        f"Need: {need}\n"
        f"AI Score: {score}/100\n\n"
        f"Recommended action: Schedule discovery call."
    )
    return _log(text)


def notify(text: str) -> dict:
    return _log(text)


def _log(text: str) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "channel": "#sales-leads",
        "text": text,
        "provider": "mock",
        "status": "sent",
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record
