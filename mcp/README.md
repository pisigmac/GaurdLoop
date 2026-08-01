# GuardLoop MCP Server

Expose GuardLoop as MCP tools for Cursor, Claude Desktop, Claude Code, and any MCP client.

## Install

```bash
cd mcp
pip install -e .
```

## Configure

Set environment variables:

```bash
export GUARDLOOP_API_URL="http://localhost:8000"
export GUARDLOOP_API_KEY="your-api-key"
```

## Add to Cursor

Add to your Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "guardloop": {
      "command": "guardloop-mcp",
      "env": {
        "GUARDLOOP_API_URL": "http://localhost:8000",
        "GUARDLOOP_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Add to Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "guardloop": {
      "command": "guardloop-mcp",
      "env": {
        "GUARDLOOP_API_URL": "http://localhost:8000",
        "GUARDLOOP_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|---|---|
| `guardloop_score_task` | Calculate 0-100 confidence score |
| `guardloop_scrub_context` | Scan text for PII/secrets |
| `guardloop_verify_browser` | Queue browser verification |
| `guardloop_get_task_status` | Check task status and loops |
| `guardloop_list_agents` | List registered agents |
| `guardloop_create_task` | Create a new task |
| `guardloop_override_score` | Override score decision |

## Usage in Cursor/Claude

Once configured, your agent can call:

```
Before I send this prompt to the LLM, let me scrub it for PII.
[Calls guardloop_scrub_context]

The context was clean. Now let me score the task before merging.
[Calls guardloop_score_task]

Score is 87 (human_review). I should flag this for the engineer.
```
