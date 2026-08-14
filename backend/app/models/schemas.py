from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Department = Literal["sales", "finance", "operations"]
Priority = Literal["low", "medium", "high"]
Sentiment = Literal["positive", "neutral", "negative"]


class RequestIntake(BaseModel):
    """Raw request coming from the webhook form (or, later, Gmail)."""

    name: str
    email: str
    company: str | None = None
    message: str


class AIAnalysisLLM(BaseModel):
    """Wire schema for Gemini structured output.

    Gemini's response_schema rejects Optional/nullable fields (anyOf with a
    NULL branch) — it returns a misleading 503 "high demand" error instead
    of a schema error. So company_size/budget use 0 as the "not mentioned"
    sentinel here, and get converted to real None in AIAnalysis via
    lead_scoring.analyze_request.
    """

    department: Department
    intent: str = Field(description="Short label, e.g. request_demo, support_question, complaint")
    lead_score: int = Field(ge=0, le=100)
    priority: Priority
    company_size: int = Field(description="Number of employees mentioned, or 0 if not mentioned")
    budget: float = Field(description="Budget in EUR mentioned, or 0 if not mentioned")
    need: str
    sentiment: Sentiment
    next_action: str
    reasoning: str = Field(description="One sentence explaining the classification")


class AIAnalysis(BaseModel):
    """Structured, DB/API-facing analysis (company_size/budget are proper Optionals)."""

    department: Department
    intent: str
    lead_score: int = Field(ge=0, le=100)
    priority: Priority
    company_size: int | None = None
    budget: float | None = None
    need: str
    sentiment: Sentiment
    next_action: str
    reasoning: str

    @classmethod
    def from_llm(cls, llm: "AIAnalysisLLM") -> "AIAnalysis":
        data = llm.model_dump()
        data["company_size"] = data["company_size"] or None
        data["budget"] = data["budget"] or None
        return cls(**data)


class EmailDraft(BaseModel):
    """LLM output when drafting the auto-response email."""

    body: str = Field(description="Full email body, ready to send, no subject line")
    confidence: float = Field(ge=0, le=1, description="How well the reply is grounded in the provided company context")


class KnowledgeSearchRequest(BaseModel):
    query: str
    department: Department | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    source_path: str
    department: str
    content: str
    similarity: float


class AnalyzeResponse(BaseModel):
    lead_id: int
    analysis: AIAnalysis
    context_used: list[KnowledgeSearchResult]
    ai_generated_email: str
    confidence: float
    decision: Literal["auto_send", "human_approval"]
    email_result: dict
    slack_result: dict | None = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: str
    company: str | None
    department: str | None
    intent: str | None
    lead_score: int | None
    priority: str | None
    budget: float | None
    need: str | None
    status: str
    confidence: float | None
    requires_approval: bool
    replied: bool
    followup_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FollowupResult(BaseModel):
    lead_id: int
    action: Literal["skipped_replied", "skipped_not_due", "followup_sent"]
    email_result: dict | None = None


class AnalyticsResponse(BaseModel):
    requests_processed: int
    automatically_resolved: int
    automation_rate: float
    average_ai_cost: float
    manual_minutes_before: float
    manual_minutes_after: float
    estimated_hours_saved_month: float
    estimated_saving_month_eur: float
    workflow_success_rate: float
    note: str = "Simulated demo metrics — no real production traffic."
