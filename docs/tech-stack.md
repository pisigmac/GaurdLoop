# Tech Stack

## Backend

| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI | Async native, auto OpenAPI, Python ecosystem |
| ORM | SQLAlchemy 2.0 (async) | Mature, type-safe, Alembic migrations |
| Database | Postgres 15 | JSONB for flexible agent configs, ACID for scores |
| Cache/Queue | Redis 7 | Pub/sub for SSE, task queue, session cache |
| Auth | Clerk | JWT, org management, SSO ready |
| PII | Microsoft Presidio | Production-grade NER + custom regex |
| Browser | Playwright | Headless Chromium, a11y, screenshots |
| Testing | pytest + pytest-asyncio | Async test support |

## Frontend

| Layer | Technology | Reason |
|---|---|---|
| Framework | Next.js 14 App Router | SSR, API routes, Vercel-ready |
| Styling | Tailwind CSS | Utility-first, design system enforcement |
| UI | shadcn/ui patterns | Accessible, composable |
| Font | Inter | Clean, readable, system-ui fallback |
| Charts | Recharts | React-native, lightweight |
| Auth | @clerk/nextjs | Seamless integration |

## SDK

| Layer | Technology | Reason |
|---|---|---|
| HTTP | urllib (stdlib) | Zero external dependencies |
| Models | dataclasses | Lightweight, type-safe |
| Testing | pytest | Standard Python testing |

## MCP Server

| Layer | Technology | Reason |
|---|---|---|
| Protocol | MCP (Model Context Protocol) | Native Cursor/Claude support |
| Server | mcp Python SDK | Official implementation |
| Transport | stdio | Standard MCP transport |

## Webhook Bridge

| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI | Async, lightweight relay |
| HTTP | httpx | Async HTTP client |
| Retry | asyncio | Exponential backoff |

## CLI

| Layer | Technology | Reason |
|---|---|---|
| Framework | Click | Mature, composable, help generation |
| HTTP | urllib (stdlib) | Zero external deps for basic ops |
| Config | JSON + pathlib | Simple, portable, 0600 permissions |
| Testing | pytest | Standard Python testing |

## Billing

| Layer | Technology | Reason |
|---|---|---|
| Payments | Stripe | Industry standard, webhooks, subscriptions |
| Checkout | Stripe Checkout | Hosted, PCI compliant |
| Portal | Stripe Billing Portal | Self-service subscription management |

## API Keys

| Layer | Technology | Reason |
|---|---|---|
| Storage | SHA-256 hash | Never store plaintext keys |
| Prefix | First 8 chars | Display without exposing full key |
| Scopes | Comma-separated | Simple RBAC |

## Rate Limiting

| Layer | Technology | Reason |
|---|---|---|
| Algorithm | Token bucket | Burst-friendly, fair |
| Backend | Redis | Fast, distributed |
| Tiers | Config per plan | Free/Pro/Enterprise differentiation |

## Webhook Worker

| Layer | Technology | Reason |
|---|---|---|
| Scheduler | asyncio loop | Lightweight, no Celery dependency |
| Retry | Exponential backoff + jitter | Prevents thundering herd |
| Batch | Configurable size | Memory-efficient |

## Email

| Layer | Technology | Reason |
|---|---|---|
| Backends | Postmark, Resend, SMTP, Console | Flexibility per environment |
| Templates | Jinja2 | Powerful, standard |
| Types | Welcome, Alert, Digest, Invoice, Blocked | Full lifecycle coverage |

## Infrastructure

| Layer | Technology | Reason |
|---|---|---|
| Container | Docker | Local dev parity |
| Orchestration | Kubernetes | Production scaling, self-hosted option |
| Ingress | nginx-ingress + cert-manager | TLS termination, rate limiting |
| Monitoring | Sentry + Prometheus | Error tracking + metrics |
| Payments | Stripe | Subscriptions, usage-based billing |
