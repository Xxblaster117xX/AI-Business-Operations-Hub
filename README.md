# AI Business Operations Hub

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-009688) ![n8n](https://img.shields.io/badge/n8n-orchestration-EA4B71) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791) ![Gemini](https://img.shields.io/badge/Gemini-API-4285F4) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED) ![License](https://img.shields.io/badge/license-MIT-green)

An autonomous system that simulates how a small company handles the
constant stream of requests hitting sales, finance, and ops — from a lead
asking for pricing to a customer asking about a refund policy. It reads the
raw message, classifies it, retrieves grounded context from the company's
own knowledge base (RAG), decides what to do, and executes it — with a
human-approval guardrail whenever the AI isn't confident enough to act
alone.

Built as a portfolio project to demonstrate **AI automation engineering**:
knowing when to reach for low-code orchestration (n8n) versus real code
(Python/FastAPI) for the actual business logic, designing AI guardrails
that hold back low-confidence actions instead of blindly automating
everything, and thinking in terms of measurable ROI, not just "it works."

```
Form ──▶ n8n (orchestration) ──▶ FastAPI backend (AI + RAG + business logic)
                                       │
                          Gemini classification + embeddings
                                       │
                              pgvector knowledge search
                                       │
                     decision: auto-send  or  human approval
                                       │
                     PostgreSQL (leads/CRM) + mock Gmail/Slack logs
                                       │
                              /api/analytics (ROI metrics)
```

## Demo

<!-- Add 1-2 screenshots or a short GIF here: the intake form with an AI
     analysis result, and/or the n8n workflow canvas. -->
<img width="1447" height="697" alt="image" src="https://github.com/user-attachments/assets/b1071540-37bb-4835-9cf4-d1d162cfab1e" />
<img width="1527" height="812" alt="image" src="https://github.com/user-attachments/assets/800986c7-f740-46f4-b558-1b8608389f5e" />
<img width="1365" height="821" alt="image" src="https://github.com/user-attachments/assets/41e2f563-798e-43c3-a552-915e19229e54" />





## Stack

- **Orchestration**: n8n
- **AI**: Gemini API (`gemini-2.5-flash` for classification/generation,
  `gemini-embedding-001` for RAG embeddings)
- **Backend**: Python, FastAPI, Pydantic
- **RAG**: PostgreSQL + pgvector
- **Integrations**: simulated Gmail/Slack (logged to `logs/`), real CRM =
  PostgreSQL itself
- **Infra**: Docker Compose
- **Tests**: pytest (Gemini calls mocked — no API key needed to run tests)

## Requirements

- Docker Desktop
- A Gemini API key (already in `.env` — **do not commit this file**)

## 1. Start the stack

```bash
docker compose up -d --build
```

This brings up:
- `postgres` (pgvector) on `localhost:5432`
- `backend` (FastAPI) on `localhost:8000` — docs at `/docs`
- `n8n` on `localhost:5679`

## 2. Ingest the company knowledge base

The sample docs live in `company-knowledge/` (sales, finance, operations).
Chunk + embed + load them into pgvector:

```bash
docker compose exec backend python -m app.rag.ingest
```

Re-run this any time you edit the markdown files.

## 3. Import the n8n workflows

Open http://localhost:5679, then import the three files in
`n8n/workflows/` (see `n8n/README.md` for details on each one). Activate
**01 - Intake & Classification** — it exposes a webhook at
`http://localhost:5679/webhook/intake`.

## 4. Try it

Open `public/index.html` directly in a browser (or serve it) and submit a
request — e.g.:

> We have around 50 sales representatives and we're looking for an AI
> system to automate lead qualification. Budget is around €15,000.

You'll see the structured AI output live: department, intent, lead score,
priority, the RAG-grounded auto-generated email, and whether it was
auto-sent or routed for human approval.

Or call the backend directly:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"name":"John Smith","email":"john@company.com","company":"Acme","message":"We have around 50 sales representatives and need to automate lead qualification. Budget ~€15,000."}'
```

Check the results:
- `GET /api/leads` — everything written to the "CRM" (Postgres)
- `GET /api/analytics` — automation rate, avg AI cost, estimated time/€ saved
- `logs/emails.log`, `logs/slack.log` — simulated outbound messages

## Project layout

```
backend/app/
  api/            FastAPI routes (analyze, knowledge, leads, analytics, notify)
  services/       lead_scoring, knowledge (RAG + email drafting), followup, analytics, cost
  rag/            embeddings, retrieval, ingest
  integrations/   email_client, slack_client, crm — all mocked, swap-in points documented inline
  models/         Pydantic schemas + SQLAlchemy models
company-knowledge/ sample sales/finance/operations docs used for RAG
n8n/workflows/    3 importable, modular workflows
public/index.html simulated intake form
db/init.sql       pgvector schema bootstrap
```

## Design notes

- **AI guardrails**: every auto-generated email carries a `confidence`
  score from the LLM. Below `CONFIDENCE_THRESHOLD` (default 0.90, see
  `.env`), the system marks the lead `requires_approval=true` instead of
  sending — see `backend/app/api/routes_analyze.py`.
- **Modularity**: n8n stays thin (validation + orchestration); all AI/business
  logic is Python, callable independently of n8n via plain HTTP endpoints
  (`/api/analyze`, `/api/knowledge/search`, `/api/leads/{id}/followup`,
  `/api/notify/slack`) — each maps to a reusable "subworkflow" concept.
- **Metrics are simulated**: `/api/analytics` computes real ratios from
  whatever traffic you generate, but the manual-time-baseline and
  hourly-rate assumptions behind the €-saved figure are illustrative
  constants (documented in `backend/app/services/analytics.py` and
  `db/init.sql`), not measured data.

## Tests

```bash
docker compose exec backend pytest
```

All Gemini calls are mocked, so this needs no network access or API key.
