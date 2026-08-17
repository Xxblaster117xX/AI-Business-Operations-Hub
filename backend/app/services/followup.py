import json
from datetime import datetime, timezone

from google.genai import types
from sqlalchemy.orm import Session

from app.config import settings
from app.gemini_client import call_with_retry, get_client
from app.integrations import email_client
from app.models.db_models import Lead
from app.models.schemas import EmailDraft, FollowupResult

FOLLOWUP_SYSTEM_PROMPT = """You are writing a polite, low-pressure follow-up email.
The recipient has not replied since their original message below. Reference their
original need briefly, offer to help further, and make it easy to say "not now".
Keep it under 80 words, no subject line. Confidence should reflect how safe this
generic follow-up is to send automatically (usually high, e.g. 0.9+, since it makes
no new factual claims).

Respond with JSON only, matching the given schema exactly.
"""


def _draft_followup(lead: Lead) -> EmailDraft:
    client = get_client()
    prompt = (
        f"{FOLLOWUP_SYSTEM_PROMPT}\n\n"
        f"Name: {lead.name}\n"
        f"Original message: {lead.message}\n"
        f"Classified need: {lead.need}\n"
    )
    response = call_with_retry(
        lambda: client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EmailDraft,
                temperature=0.4,
            ),
        )
    )
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, EmailDraft):
        return parsed
    return EmailDraft.model_validate(json.loads(response.text))


def check_and_followup(db: Session, lead: Lead) -> FollowupResult:
    if lead.replied:
        return FollowupResult(lead_id=lead.id, action="skipped_replied")

    if lead.followup_sent:
        return FollowupResult(lead_id=lead.id, action="skipped_already_sent")

    now = datetime.now(timezone.utc)
    due = lead.next_followup_at is None or lead.next_followup_at <= now
    if not due:
        return FollowupResult(lead_id=lead.id, action="skipped_not_due")

    draft = _draft_followup(lead)
    email_result = email_client.send_email(
        to=lead.email,
        subject=f"Following up — {lead.need or 'your request'}",
        body=draft.body,
    )

    lead.followup_sent = True
    lead.status = "followed_up"
    db.commit()

    return FollowupResult(lead_id=lead.id, action="followup_sent", email_result=email_result)
