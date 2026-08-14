from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.db import Base


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_path: Mapped[str] = mapped_column(Text)
    department: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    company: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text)

    department: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent: Mapped[str | None] = mapped_column(Text, nullable=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    need: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(Text, default="new")
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    replied: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    next_followup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RequestLog(Base):
    __tablename__ = "request_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endpoint: Mapped[str] = mapped_column(Text)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    manual_minutes_baseline: Mapped[float] = mapped_column(Numeric, default=8)
    manual_minutes_actual: Mapped[float] = mapped_column(Numeric, default=1.7)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
