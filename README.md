<div align="center">

# 🛡️ GuardLoop
### *The Autonomous AI Agent Governance, Observability & Safety Platform*

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](backend)
[![Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014-000000.svg?logo=next.js)](frontend)
[![Docker](https://img.shields.io/badge/Containerized-Docker-2496ED.svg?logo=docker)](docker-compose.yml)
[![Python SDK](https://img.shields.io/badge/SDK-Python-3776AB.svg?logo=python)](sdk)

**Deploy Autonomous AI Agents with Zero Regrets.**

[Key Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [SDK & MCP](#-sdk--mcp-integration) • [Roadmap](#-roadmap)

---

</div>

## 🌟 Why GuardLoop?

As AI coding agents (Cursor, Claude Code, GitHub Copilot, Aider, Windsurf) gain execution autonomy, engineering teams face critical risks: **uncontrolled infinite loops**, **hardcoded secret leaks**, **untested pull requests**, and **broken dependency chains**.

**GuardLoop** sits between your AI agent fleet and your codebase as a **real-time governance & orchestration control plane**. It continuously monitors agent actions, redacts sensitive credentials, calculates multi-dimensional trust scores, and automatically gates deployments.

---

## ⚡ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>🔄 Real-Time Loop Monitor</h3>
      <p>Detects runaway iterations, stuck action loops, agent drift, and context window bloat before AI agents exhaust your token budget or corrupt files.</p>
    </td>
    <td width="50%">
      <h3>🔒 Zero-Trust PII & Secret Redaction</h3>
      <p>Automatically scans and scrubs credit cards, SSNs, Stripe keys, AWS secrets, and JWT tokens in real time before context reaches third-party LLMs.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📊 0-100 Confidence Score Engine</h3>
      <p>Evaluates unit test pass rates, AST coverage, security vulnerabilities, and behavior. Automatically triggers <code>auto_approve</code>, <code>human_review</code>, or <code>block</code>.</p>
    </td>
    <td width="50%">
      <h3>🔀 DAG Task Dependency Scheduler</h3>
      <p>Orchestrates complex multi-agent workflows into Directed Acyclic Graphs. Computes critical paths and enforces prerequisite task ordering.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🌐 Headless Browser Verification</h3>
      <p>Dispatches isolated Playwright headless browser containers to interactively validate frontend UI rendering, dynamic clicks, and layout stability.</p>
    </td>
    <td width="50%">
      <h3>📡 Live Event Stream & Dashboard</h3>
      <p>High-performance Server-Sent Events (SSE) stream and modern dark-mode Web UI dashboard for real-time fleet observability.</p>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

Get GuardLoop up and running locally in **under 2 minutes** using Docker Compose:

```bash
# 1. Clone repository
git clone https://github.com/pisigmac/GaurdLoop.git
cd GuardLoop

# 2. Launch GuardLoop services (Backend, Frontend, Postgres, Redis)
docker compose up --build -d
```

| Service | Local URL | Description |
| :--- | :--- | :--- |
| 📊 **GuardLoop Web UI** | [http://localhost:33000](http://localhost:33000) | Observability Dashboard, DAG Visualizer & Live Monitor |
| ⚡ **FastAPI Backend** | [http://localhost:38000](http://localhost:38000) | REST API & SSE Server |
| 📖 **Interactive API Docs** | [http://localhost:38000/docs](http://localhost:38000/docs) | OpenAPI / Swagger Documentation |

---

## 💻 SDK & MCP Integration

### 🐍 Python SDK

Integrate GuardLoop into custom Python AI workflows in 3 lines:

```python
from guardloop_sdk import GuardLoopClient

client = GuardLoopClient(api_key="gl_live_secret_key")

# 1. Create a task for an AI agent
task = client.tasks.create(
    name="Implement SHA-256 password hashing",
    priority=9,
    output={"tests_passed": 42, "line_coverage": 0.95}
)

# 2. Calculate real-time confidence score
score = client.tasks.score(task.id)
print(f"Overall Score: {score.overall} → Gate Decision: {score.decision}")
# Output: Overall Score: 99 → Gate Decision: auto_approve
```

### 🔌 Model Context Protocol (MCP) Server

Connect GuardLoop directly to **Cursor** or **Claude Desktop**:

```json
{
  "mcpServers": {
    "guardloop": {
      "command": "guardloop-mcp",
      "env": {
        "GUARDLOOP_API_URL": "http://localhost:38000",
        "GUARDLOOP_API_KEY": "gl_mcp_key"
      }
    }
  }
}
```

---

## 🏗️ Architecture

```text
               ┌──────────────────────────────────────────────┐
               │    AI Agent Fleet (Cursor / Claude / Copilot) │
               └──────────────────────┬───────────────────────┘
                                      │ Webhooks / MCP / SDK
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          GuardLoop FastAPI Engine             │
               │   (LoopMonitor · ContextScrub · ScoreEngine) │
               └──────────────┬───────────────┬───────────────┘
                              │               │
                     ┌────────┴───────┐     ┌─┴──────────────┐
                     │ PostgreSQL 15  │     │ Redis Pub/Sub  │
                     │ (Persistence)  │     │ (Real-time SSE)│
                     └────────────────┘     └────────┬───────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────┐
                                      │ Next.js 14 Dashboard │
                                      │ (http://localhost:33000)
                                      └──────────────────────┘
```

---

## 🛠️ CLI Tool

Control your GuardLoop governance server directly from the terminal:

```bash
cd cli
pip install -e .

# Authenticate & list active tasks
guardloop auth login
guardloop task list --status running
```

---

## 🗺️ Roadmap

Looking for what's coming next? Read our full [**FUTURE.md**](FUTURE.md) roadmap covering:
- 🛑 **Human-in-the-Loop (HITL) Approval Prompts**
- 📦 **Docker/gVisor Micro-Sandbox Execution**
- 🤖 **Agent Debate & Consensus Voting Engine**
- 🔑 **Automated Secret Revocation Webhooks**
- 🧩 **VS Code & Cursor IDE Extensions**

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
