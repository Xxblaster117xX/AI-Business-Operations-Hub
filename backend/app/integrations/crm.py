"""The 'CRM' in this project is PostgreSQL itself — no external CRM SaaS is
needed for the demo. This module is the thin write/read layer other services
call, so swapping in a real CRM (HubSpot, Salesforce...) later only means
changing these functions, not their callers.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.db_models import Lead
from app.models.schemas import AIAnalysis, RequestIntake

FOLLOWUP_DELAY_HOURS = 48


def create_lead(
    db: Session,
    intake: RequestIntake,
    analysis: AIAnalysis,
    ai_response: str,
    confidence: float,
    requires_approval: bool,
) -> Lead:
    lead = Lead(
        name=intake.name,
        email=intake.email,
        company=intake.company,
        message=intake.message,
        department=analysis.department,
        intent=analysis.intent,
        lead_score=analysis.lead_score,
        priority=analysis.priority,
        company_size=analysis.company_size,
        budget=analysis.budget,
        need=analysis.need,
        sentiment=analysis.sentiment,
        next_action=analysis.next_action,
        status="priority_crm" if analysis.lead_score >= 80 else "normal_crm",
        ai_response=ai_response,
        confidence=confidence,
        requires_approval=requires_approval,
        next_followup_at=datetime.now(timezone.utc) + timedelta(hours=FOLLOWUP_DELAY_HOURS),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
