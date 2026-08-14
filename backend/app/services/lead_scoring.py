import json

from google.genai import types

from app.config import settings
from app.gemini_client import call_with_retry, get_client
from app.models.schemas import AIAnalysis, AIAnalysisLLM, RequestIntake

SYSTEM_PROMPT = """You are the intake classifier for an AI Business Operations Hub.
You receive raw messages from prospects, customers, or internal employees and must
turn them into structured data so the right department can act on them.

Rules:
- department is "sales" for new business / demo / pricing / lead requests,
  "finance" for invoicing, payment, policy, or refund questions,
  "operations" for support, escalations, or process questions.
- lead_score (0-100) estimates commercial value: weigh stated budget, company size,
  urgency, and buying intent. Support/finance requests with no purchase intent should
  score low (0-30).
- priority is "high" if lead_score >= 80 or the message signals urgency/escalation,
  "medium" for 40-79, otherwise "low".
- Extract company_size and budget as numbers when mentioned (budget in EUR), else 0.
- next_action is a short actionable instruction, e.g. "schedule_meeting",
  "send_pricing_info", "escalate_to_human", "send_policy_summary".
- reasoning is one short sentence justifying the classification.

Respond with JSON only, matching the given schema exactly.
"""


def analyze_request(intake: RequestIntake) -> tuple[AIAnalysis, int, int]:
    """Classify a raw request into structured fields. Returns (analysis, tokens_in, tokens_out)."""
    client = get_client()

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Name: {intake.name}\n"
        f"Company: {intake.company or 'unknown'}\n"
        f"Message:\n{intake.message}"
    )

    response = call_with_retry(
        lambda: client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIAnalysisLLM,
                temperature=0.2,
            ),
        )
    )

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, AIAnalysisLLM):
        llm_analysis = parsed
    else:
        llm_analysis = AIAnalysisLLM.model_validate(json.loads(response.text))
    analysis = AIAnalysis.from_llm(llm_analysis)

    usage = getattr(response, "usage_metadata", None)
    tokens_in = getattr(usage, "prompt_token_count", 0) or 0
    tokens_out = getattr(usage, "candidates_token_count", 0) or 0
    return analysis, tokens_in, tokens_out
