# Standard Operating Procedures

## New customer onboarding
1. Discovery workshop scheduled within 3 business days of contract signature.
2. Knowledge base ingestion: customer provides source docs, we chunk and
   embed them within 48h.
3. Workflow configuration and testing in a staging environment.
4. Go-live with a 2-week monitored ramp-up period (all AI actions require
   human approval during ramp-up regardless of confidence score).
5. Handover to standard operations after ramp-up review.

## Handling a general operations request
- Classify the request (bug report, process question, feature request,
  access request).
- Check the knowledge base for an existing documented answer.
- If found and confidence is high, answer directly.
- If not found, or the request involves account access/security, escalate
  per the escalation policy.
