import pytest
from pydantic import ValidationError

from app.models.schemas import AIAnalysis, EmailDraft, RequestIntake


def test_ai_analysis_accepts_valid_payload():
    analysis = AIAnalysis(
        department="sales",
        intent="request_demo",
        lead_score=91,
        priority="high",
        company_size=50,
        budget=15000,
        need="AI lead qualification",
        sentiment="positive",
        next_action="schedule_meeting",
        reasoning="Clear budget and buying intent stated.",
    )
    assert analysis.lead_score == 91
    assert analysis.department == "sales"


def test_ai_analysis_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        AIAnalysis(
            department="sales",
            intent="request_demo",
            lead_score=150,
            priority="high",
            need="x",
            sentiment="positive",
            next_action="schedule_meeting",
            reasoning="x",
        )


def test_ai_analysis_rejects_invalid_department():
    with pytest.raises(ValidationError):
        AIAnalysis(
            department="marketing",
            intent="x",
            lead_score=10,
            priority="low",
            need="x",
            sentiment="neutral",
            next_action="x",
            reasoning="x",
        )


def test_email_draft_confidence_bounds():
    with pytest.raises(ValidationError):
        EmailDraft(body="hi", confidence=1.5)


def test_request_intake_requires_message():
    with pytest.raises(ValidationError):
        RequestIntake(name="John", email="john@company.com")
