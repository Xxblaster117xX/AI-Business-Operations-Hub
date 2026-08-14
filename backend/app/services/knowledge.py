import json

from google.genai import types
from sqlalchemy.orm import Session

from app.config import settings
from app.gemini_client import call_with_retry, get_client
from app.models.schemas import AIAnalysis, EmailDraft, KnowledgeSearchResult, RequestIntake
from app.rag.retrieval import search

EMAIL_SYSTEM_PROMPT = """You are drafting a first-response email on behalf of an AI
Business Operations Hub. Use ONLY the company context provided below to make claims
about pricing, services, or policy — never invent numbers or promises that aren't
in the context. Keep the tone professional, warm, and concise (under 150 words).
Address the person by name. Do not include a subject line.

Also return a confidence score (0-1): how well the provided context actually covers
what this person is asking. If the context is thin or off-topic, give a low score.

Respond with JSON only, matching the given schema exactly.
"""


def retrieve_context(db: Session, intake: RequestIntake, analysis: AIAnalysis) -> list[KnowledgeSearchResult]:
    query = f"{analysis.need}. {intake.message}"
    return search(db, query=query, department=analysis.department, top_k=4)


def draft_email(intake: RequestIntake, analysis: AIAnalysis, context: list[KnowledgeSearchResult]) -> EmailDraft:
    client = get_client()

    context_block = "\n\n".join(f"[{c.source_path}]\n{c.content}" for c in context) or "(no relevant context found)"

    prompt = (
        f"{EMAIL_SYSTEM_PROMPT}\n\n"
        f"--- COMPANY CONTEXT ---\n{context_block}\n\n"
        f"--- REQUEST ---\n"
        f"From: {intake.name} ({intake.company or 'unknown company'})\n"
        f"Message: {intake.message}\n"
        f"Classified need: {analysis.need}\n"
        f"Department: {analysis.department}\n"
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
