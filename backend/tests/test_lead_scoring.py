from types import SimpleNamespace

from app.models.schemas import AIAnalysisLLM, RequestIntake
from app.services import lead_scoring


def _fake_response(parsed=None, text=None, tokens_in=120, tokens_out=40):
    return SimpleNamespace(
        parsed=parsed,
        text=text,
        usage_metadata=SimpleNamespace(prompt_token_count=tokens_in, candidates_token_count=tokens_out),
    )


def test_analyze_request_uses_parsed_response(mocker):
    llm_output = AIAnalysisLLM(
        department="sales",
        intent="request_demo",
        lead_score=91,
        priority="high",
        company_size=50,
        budget=15000,
        need="AI lead qualification",
        sentiment="positive",
        next_action="schedule_meeting",
        reasoning="Budget and intent are explicit.",
    )
    fake_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=mocker.Mock(return_value=_fake_response(parsed=llm_output)))
    )
    mocker.patch("app.services.lead_scoring.get_client", return_value=fake_client)

    intake = RequestIntake(
        name="John Smith",
        email="john@company.com",
        company="Acme",
        message="We have 50 sales reps and need AI lead qualification. Budget ~€15,000.",
    )

    analysis, tokens_in, tokens_out = lead_scoring.analyze_request(intake)

    assert analysis.department == "sales"
    assert analysis.lead_score == 91
    assert analysis.company_size == 50
    assert analysis.budget == 15000
    assert tokens_in == 120
    assert tokens_out == 40


def test_analyze_request_falls_back_to_json_text(mocker):
    payload = {
        "department": "finance",
        "intent": "policy_question",
        "lead_score": 15,
        "priority": "low",
        "company_size": 0,
        "budget": 0,
        "need": "Return policy for enterprise client",
        "sentiment": "neutral",
        "next_action": "send_policy_summary",
        "reasoning": "No purchase intent, informational request.",
    }
    import json

    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=mocker.Mock(return_value=_fake_response(parsed=None, text=json.dumps(payload)))
        )
    )
    mocker.patch("app.services.lead_scoring.get_client", return_value=fake_client)

    intake = RequestIntake(name="Jane", email="jane@company.com", message="What is our return policy?")
    analysis, _, _ = lead_scoring.analyze_request(intake)

    assert analysis.department == "finance"
    assert analysis.lead_score == 15
    assert analysis.company_size is None
    assert analysis.budget is None
