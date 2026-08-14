import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.integrations import crm, email_client, slack_client
from app.models.db_models import RequestLog
from app.models.schemas import AnalyzeResponse, RequestIntake
from app.services import knowledge
from app.services.cost import estimate_cost_eur
from app.services.lead_scoring import analyze_request

router = APIRouter()


@router.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(intake: RequestIntake, db: Session = Depends(get_db)) -> AnalyzeResponse:
    start = time.perf_counter()
    success = True
    tokens_in = tokens_out = 0
    lead = None

    try:
        analysis, tin, tout = analyze_request(intake)
        tokens_in += tin
        tokens_out += tout

        context = knowledge.retrieve_context(db, intake, analysis)
        draft = knowledge.draft_email(intake, analysis, context)

        decision = "auto_send" if draft.confidence >= settings.confidence_threshold else "human_approval"
        requires_approval = decision == "human_approval"

        lead = crm.create_lead(
            db,
            intake=intake,
            analysis=analysis,
            ai_response=draft.body,
            confidence=draft.confidence,
            requires_approval=requires_approval,
        )

        email_result = {"status": "pending_human_approval"}
        if decision == "auto_send":
            email_result = email_client.send_email(
                to=intake.email,
                subject=f"Re: {analysis.need}",
                body=draft.body,
            )

        slack_result = None
        if analysis.lead_score >= 80:
            slack_result = slack_client.notify_high_value_lead(
                company=intake.company,
                name=intake.name,
                budget=analysis.budget,
                need=analysis.need,
                score=analysis.lead_score,
            )

        return AnalyzeResponse(
            lead_id=lead.id,
            analysis=analysis,
            context_used=context,
            ai_generated_email=draft.body,
            confidence=draft.confidence,
            decision=decision,
            email_result=email_result,
            slack_result=slack_result,
        )
    except Exception:
        success = False
        raise
    finally:
        latency_ms = int((time.perf_counter() - start) * 1000)
        db.add(
            RequestLog(
                endpoint="analyze",
                lead_id=lead.id if lead is not None else None,
                latency_ms=latency_ms,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                estimated_cost=estimate_cost_eur(tokens_in, tokens_out),
                success=success,
            )
        )
        db.commit()
