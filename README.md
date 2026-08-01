# GuardLoop

**Agent Trust & Orchestration Layer**

GuardLoop sits on top of Cursor, Claude Code, GitHub Copilot, and custom agents to verify, score, and gate their output before it reaches production.

## What It Does

- **TaskGraph Engine** — Dependency-aware DAG scheduling with critical path analysis
- **ScoreEngine** — 0-100 confidence score from tests, coverage, security, and behavior
- **ContextScrub** — Real-time PII and secret redaction before every LLM call
- **BrowserVerify** — Headless Playwright validation for UI changes
- **LoopMonitor** — Detects infinite loops, context bloat, and agent drift
- **Multi-Agent** — Pluggable adapters for Cursor, Claude Code, GitHub Copilot

## SDK

```python
from guardloop_sdk import GuardLoopClient

client = GuardLoopClient(api_key="gl_...")
task = client.tasks.create(name="Refactor auth", agent_id="abc123")
score = client.tasks.score(task.id)
print(f"Score: {score.overall} — {score.decision}")
```

## MCP Server

Add to Cursor MCP settings:
```json
{
  "mcpServers": {
    "guardloop": {
      "command": "guardloop-mcp",
      "env": { "GUARDLOOP_API_URL": "http://localhost:8000", "GUARDLOOP_API_KEY": "..." }
    }
  }
}
```

## Quick Start

```bash
git clone https://github.com/your-org/guardloop.git
cd guardloop
docker-compose up --build
```

- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Architecture

```
Frontend (Next.js 14 + Tailwind)  <--SSE-->  Backend (FastAPI + SQLAlchemy async)
                                                    |
                    Redis (pub/sub + queue) <------+------> Postgres 15
                                                    |
                    BrowserVerify (Playwright containers)
```

## CLI Tool

Install the CLI to control GuardLoop from your terminal:

```bash
cd cli
pip install -e .
guardloop auth login
guardloop task list --status running
```

## Project Structure

```
guardloop/
├── backend/          FastAPI, async SQLAlchemy, services
├── cli/              Python CLI (Click) — 14 commands
├── sdk/              Python SDK — programmatic API access
├── mcp/              MCP Server — Cursor/Claude Desktop integration
├── bridge/           Webhook Bridge — relay agent webhooks to GuardLoop
├── frontend/          FastAPI, async SQLAlchemy, services
├── frontend/         Next.js 14, shadcn/ui patterns
├── infra/            Docker + K8s manifests
├── docs/             Full documentation
└── ops/              Runbooks and operational docs
```

## License

MIT
