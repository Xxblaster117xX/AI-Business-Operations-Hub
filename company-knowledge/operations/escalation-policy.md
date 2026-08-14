# Escalation Policy

## Always escalate to a human, never automate
- Legal threats or mentions of litigation
- Security incidents or suspected data breaches
- Payment disputes and chargebacks
- Enterprise (Scale tier) refund requests
- Any request where AI confidence is below 0.90

## Escalation SLAs
- Critical (security, legal, active outage): acknowledge within 1 hour
- High (angry customer, at-risk renewal): acknowledge within 4 business hours
- Normal: acknowledge within 1 business day

## Escalation routing
- Security/legal: escalate to founders directly
- Finance disputes: escalate to finance lead
- Product/technical: escalate to on-call engineer via Slack
- Everything else: escalate to the customer success channel
