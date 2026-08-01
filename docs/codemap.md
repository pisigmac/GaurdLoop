# Code Map

## Backend

```
backend/
├── app/
│   ├── main.py              FastAPI app, lifespan, middleware, routes
│   ├── core/
│   │   ├── config.py        Settings (Pydantic, env-driven)
│   │   ├── database.py      Async SQLAlchemy engine + session
│   │   ├── redis.py         Async Redis connection pool
│   │   └── security.py      Clerk JWT verification
│   ├── models/              SQLAlchemy ORM models (10 tables)
│   ├── schemas/             Pydantic request/response models
│   ├── services/            Core business logic
│   │   ├── taskgraph.py     DAG scheduler + critical path
│   │   ├── scoreengine.py   0-100 scoring engine
│   │   ├── contextscrub.py  PII + secret detection/redaction
│   │   ├── browserverify.py Playwright browser validation
│   │   └── loopmonitor.py   Loop/drift detection
│   ├── api/                 FastAPI route handlers
│   │   ├── tasks.py         CRUD + start + score + graph + SSE
│   │   ├── agents.py        Agent registration
│   │   ├── scores.py        Score listing + override
│   │   ├── pii.py           Context scrubbing
│   │   ├── browser.py       Browser verification queue
│   │   ├── webhooks.py      Webhook ingestion + auto-task creation
│   │   └── sse.py           Server-sent events
│   └── adapters/            Multi-agent support
│       ├── base.py          Abstract adapter interface
│       ├── cursor.py        Cursor adapter
│       ├── claude_code.py   Claude Code adapter
│       ├── github_copilot.py GitHub Copilot adapter
│       └── registry.py      Adapter factory
├── tests/                   Pytest suite
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── pytest.ini
```

## SDK

```
sdk/
├── guardloop_sdk/
│   ├── __init__.py
│   ├── client.py       Typed HTTP client with resource classes
│   ├── models.py         Dataclass models (Task, Agent, Score, PiiScan, BrowserVerify)
│   └── exceptions.py   GuardLoopError, GuardLoopAPIError, GuardLoopAuthError
├── tests/
├── setup.py
└── pyproject.toml
```

Resources: client.tasks, client.agents, client.scores, client.pii, client.browser

## MCP Server

```
mcp/
├── guardloop_mcp/
│   ├── __init__.py
│   ├── server.py       MCP server with 7 tools
│   └── client.py       Internal HTTP client
├── setup.py
└── pyproject.toml
```

Tools: guardloop_score_task, guardloop_scrub_context, guardloop_verify_browser,
guardloop_get_task_status, guardloop_list_agents, guardloop_create_task, guardloop_override_score

## Webhook Bridge

```
bridge/
├── guardloop_bridge/
│   ├── __init__.py
│   └── main.py         FastAPI relay with GitHub/Slack/Cursor endpoints
├── Dockerfile
├── setup.py
└── pyproject.toml
```

Endpoints: /webhook/{source}, /webhook/github, /webhook/slack, /webhook/cursor

## CLI

```
cli/
├── guardloop_cli/
│   ├── __init__.py
│   ├── main.py         Click CLI with 6 command groups
│   ├── api.py          HTTP client + SSE streaming
│   ├── config.py       ~/.guardloop/config.json management
│   └── utils.py        Table formatting, JSON output
├── tests/              pytest suite
├── setup.py
├── pyproject.toml
└── README.md
```

Commands: auth, task, agent, score, pii, browser, monitor, config

## Billing

```
backend/app/models/subscription.py    Subscription + Invoice models
backend/app/schemas/billing.py        Checkout + Portal session schemas
backend/app/api/billing.py            Stripe webhooks + checkout endpoints
```

## API Keys

```
backend/app/models/api_key.py         API key model with hash + prefix
backend/app/schemas/api_key.py        Create + list schemas
backend/app/api/api_keys.py           CRUD + validation middleware
```

## Rate Limiting

```
backend/app/middleware/rate_limit.py  Redis token bucket per tier
```

## Webhook Worker

```
backend/worker/main.py                Background retry with exponential backoff
backend/worker/Dockerfile             Worker container
```

## Email Service

```
backend/app/services/email.py         Postmark/Resend/SMTP backends + Jinja2 templates
```

## Frontend

```
frontend/
├── app/
│   ├── layout.tsx           Root layout (Inter font, metadata)
│   ├── globals.css          Tailwind + custom styles
│   └── (app)/               Authenticated pages
│       ├── page.tsx         Dashboard
│       ├── tasks/page.tsx   Task list
│       ├── agents/page.tsx  Agent registry
│       ├── scores/page.tsx  Score history
│       ├── browser/page.tsx Browser verification
│       ├── monitor/page.tsx Live SSE monitor
│       └── settings/page.tsx Org settings
├── components/
│   ├── app-layout.tsx       Sidebar + navigation
│   ├── score-badge.tsx      Score color badge
│   ├── status-badge.tsx     Task status badge
│   ├── decision-badge.tsx   Gate decision badge
│   └── task-graph-viz.tsx   SVG dependency graph
├── lib/
│   └── api.ts               Typed API client + SSE helper
├── package.json
├── next.config.js
├── tailwind.config.js
└── Dockerfile
```
