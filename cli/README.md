# GuardLoop CLI

Control your agent trust layer from the terminal.

## Install

```bash
cd cli
pip install -e .
```

## Usage

```bash
# Authenticate
guardloop auth login

# Tasks
guardloop task create --name "Refactor auth" --agent-id abc123
guardloop task list --status running
guardloop task start <task-id>
guardloop task score <task-id>
guardloop task stream <task-id>

# Agents
guardloop agent list
guardloop agent add --name "Cursor Prod" --type cursor --config agent.json
guardloop agent delete <agent-id>

# Scores
guardloop score list --decision block
guardloop score override <score-id> --decision auto_approve --reason "False positive"

# PII
guardloop pii scrub --task-id <id> --strict < file.txt
guardloop pii scans <task-id>

# Browser
guardloop browser verify --task-id <id> --url http://localhost:3000
guardloop browser list <task-id>

# Monitor
guardloop monitor --org-id default-org

# Config
guardloop config
```

## Environment Variables

- `GUARDLOOP_API_URL` — API base URL
- `GUARDLOOP_API_KEY` — API authentication key
