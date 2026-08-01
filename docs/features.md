# Features

## Core

| Feature | Description | Status |
|---|---|---|
| TaskGraph Engine | DAG scheduling with critical path | Shipped |
| ScoreEngine | 0-100 confidence from 4 dimensions | Shipped |
| ContextScrub | PII + secret redaction | Shipped |
| BrowserVerify | Playwright a11y + visual regression | Shipped |
| LoopMonitor | Infinite loop + drift detection | Shipped |
| Multi-Agent Adapters | Cursor, Claude Code, Copilot, OpenAI Codex, Aider, Continue.dev, Windsurf, Devin, Custom | Shipped |
| SSE Live Monitor | Real-time event streaming | Shipped |
| Python SDK | Typed models + resource classes | Shipped |
| MCP Server | 7 tools for Cursor/Claude Desktop | Shipped |
| Webhook Bridge | Relay + transform + retry | Shipped |
| Stripe Billing | Subscriptions, invoices, checkout | Shipped |
| API Key Management | Create, revoke, scope, hash | Shipped |
| Rate Limiting | Redis token bucket per tier | Shipped |
| Webhook Retry Worker | Background retry with backoff | Shipped |
| Email Service | Postmark/Resend/SMTP + templates | Shipped |
| Admin Dashboard | System overview, health, metrics | Shipped |
| Python SDK | Programmatic API with typed models | Shipped |
| MCP Server | 7 tools for Cursor/Claude Desktop | Shipped |
| Webhook Bridge | Relay + transform agent webhooks | Shipped |
| Webhook Ingest | GitHub, Slack, Linear, PagerDuty | Shipped |

## Scoring Dimensions

1. **Tests** (40%) — Pass rate, flaky detection, duration
2. **Coverage** (25%) — Line, branch, function coverage
3. **Security** (20%) — CVE scan, secret exposure, SAST
4. **Behavioral** (15%) — No infinite loops, no context bloat, browser pass

## Gate Decisions

- **Auto-approve** (>= 90): Merge without human review
- **Human review** (70-89): Flag for engineer
- **Block** (< 70): Reject, return to agent
