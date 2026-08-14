from types import SimpleNamespace

from app.models.schemas import AIAnalysis, EmailDraft, KnowledgeSearchResult, RequestIntake
from app.services import knowledge


def test_draft_email_uses_parsed_response(mocker):
    expected = EmailDraft(body="Hi John, thanks for reaching out...", confidence=0.95)
    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=mocker.Mock(return_value=SimpleNamespace(parsed=expected, text=None))
        )
    )
    mocker.patch("app.services.knowledge.get_client", return_value=fake_client)

    intake = RequestIntake(name="John", email="john@company.com", message="Tell me about pricing")
    analysis = AIAnalysis(
        department="sales",
        intent="pricing_question",
        lead_score=60,
        priority="medium",
        need="Pricing info",
        sentiment="positive",
        next_action="send_pricing_info",
        reasoning="Asked about pricing directly.",
    )
    context = [
        KnowledgeSearchResult(source_path="sales/pricing.md", department="sales", content="Growth is €1200/mo", similarity=0.9)
    ]

    draft = knowledge.draft_email(intake, analysis, context)

    assert draft == expected
    fake_client.models.generate_content.assert_called_once()


def test_retrieve_context_builds_query_from_need_and_message(mocker):
    fake_results = [
        KnowledgeSearchResult(source_path="sales/pricing.md", department="sales", content="...", similarity=0.8)
    ]
    search_mock = mocker.patch("app.services.knowledge.search", return_value=fake_results)

    intake = RequestIntake(name="Jane", email="jane@company.com", message="What plans do you offer?")
    analysis = AIAnalysis(
        department="sales",
        intent="pricing_question",
        lead_score=40,
        priority="medium",
        need="Pricing plans",
        sentiment="neutral",
        next_action="send_pricing_info",
        reasoning="x",
    )

    results = knowledge.retrieve_context(db=mocker.Mock(), intake=intake, analysis=analysis)

    assert results == fake_results
    _, kwargs = search_mock.call_args
    assert kwargs["department"] == "sales"
    assert "Pricing plans" in kwargs["query"]
