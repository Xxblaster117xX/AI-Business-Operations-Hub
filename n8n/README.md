# n8n workflows

Three modular, importable workflows. Business logic (classification, RAG,
scoring, email drafting, integrations) lives in the Python backend — these
workflows are thin orchestration on top of it.

## Import

1. Open n8n at http://localhost:5679
2. Menu → Import from File → pick each `.json` file in `workflows/`
3. They call the backend via `$env.BACKEND_BASE_URL` (already set to
   `http://backend:8000` in `docker-compose.yml`)

## Workflows

- **01 - Intake & Classification** — webhook (`POST /webhook/intake`)
  receives the form submission, validates required fields, calls
  `POST /api/analyze` (classification + RAG + scoring + drafting +
  mock email/Slack all happen inside that one backend call), then branches
  visually on lead score for the demo.
- **02 - Followup Check** — runs hourly, pulls leads from
  `GET /api/leads`, and calls `POST /api/leads/{id}/followup` for anyone who
  hasn't replied. The backend itself decides whether 48h have actually
  passed (`skipped_not_due` vs `followup_sent`), so it's safe to call this
  for every unreplied lead every run.
- **03 - Analytics Digest** — runs daily at 9am, pulls
  `GET /api/analytics`, formats a summary, and posts it via
  `POST /api/notify/slack`.

## Swapping in real Gmail / Slack later

Everything here is simulated (logged to `logs/emails.log` and
`logs/slack.log` by the backend) so the whole pipeline runs with zero
external accounts. To go live:

- Replace the **Webhook** trigger in workflow 01 with a **Gmail Trigger**
  node (OAuth2), mapping subject/body/from into the same
  `{name, email, company, message}` shape.
- Implement `send_email` in `backend/app/integrations/email_client.py` using
  the Gmail API instead of the log file — no other code changes needed.
- Implement `notify` / `notify_high_value_lead` in
  `backend/app/integrations/slack_client.py` using a real Slack Incoming
  Webhook URL — same signature, same callers.
