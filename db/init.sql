-- AI Business Operations Hub — schema bootstrap
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id          SERIAL PRIMARY KEY,
    source_path TEXT NOT NULL,
    department  TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(768) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
    ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TABLE IF NOT EXISTS leads (
    id                SERIAL PRIMARY KEY,
    name              TEXT NOT NULL,
    email             TEXT NOT NULL,
    company           TEXT,
    message           TEXT NOT NULL,
    department        TEXT,
    intent            TEXT,
    lead_score        INTEGER,
    priority          TEXT,
    company_size      INTEGER,
    budget            NUMERIC,
    need              TEXT,
    sentiment         TEXT,
    next_action       TEXT,
    status            TEXT NOT NULL DEFAULT 'new',
    ai_response       TEXT,
    confidence        NUMERIC,
    requires_approval BOOLEAN NOT NULL DEFAULT false,
    replied           BOOLEAN NOT NULL DEFAULT false,
    followup_sent     BOOLEAN NOT NULL DEFAULT false,
    next_followup_at  TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS request_log (
    id               SERIAL PRIMARY KEY,
    endpoint         TEXT NOT NULL,
    lead_id          INTEGER REFERENCES leads(id),
    latency_ms       INTEGER,
    tokens_in        INTEGER,
    tokens_out       INTEGER,
    estimated_cost   NUMERIC,
    success          BOOLEAN NOT NULL DEFAULT true,
    manual_minutes_baseline NUMERIC DEFAULT 8,
    manual_minutes_actual   NUMERIC DEFAULT 1.7,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
