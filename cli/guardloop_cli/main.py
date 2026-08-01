"""GuardLoop CLI entry point."""
import click
import json
import os
import sys
from pathlib import Path
from typing import Optional

from guardloop_cli.api import GuardLoopClient
from guardloop_cli.config import Config
from guardloop_cli.utils import print_json, print_table, print_error, print_success

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option("--api-url", envvar="GUARDLOOP_API_URL", help="GuardLoop API base URL")
@click.option("--api-key", envvar="GUARDLOOP_API_KEY", help="GuardLoop API key")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.version_option(version="1.0.0", prog_name="guardloop")
@click.pass_context
def cli(ctx, config, api_url, api_key, verbose):
    """GuardLoop CLI — Agent Trust & Orchestration Layer"""
    ctx.ensure_object(Config)
    cfg = ctx.obj

    if config:
        cfg.load(config)
    if api_url:
        cfg.api_url = api_url
    if api_key:
        cfg.api_key = api_key
    if verbose:
        cfg.verbose = verbose

    cfg.validate()

# ============ AUTH ============
@cli.group()
def auth():
    """Authentication and configuration"""
    pass

@auth.command("login")
@click.option("--api-url", prompt="GuardLoop API URL", default="http://localhost:8000")
@click.option("--api-key", prompt="API Key", hide_input=True)
@pass_config
def auth_login(cfg, api_url, api_key):
    """Save credentials to config file"""
    cfg.api_url = api_url
    cfg.api_key = api_key
    cfg.save()
    print_success(f"Logged in to {api_url}")

@auth.command("whoami")
@pass_config
def auth_whoami(cfg):
    """Show current user context"""
    click.echo(f"API URL: {cfg.api_url}")
    click.echo(f"API Key: {'*' * len(cfg.api_key) if cfg.api_key else 'Not set'}")

@auth.command("logout")
@pass_config
def auth_logout(cfg):
    """Remove saved credentials"""
    cfg.clear()
    print_success("Logged out")

# ============ TASKS ============
@cli.group()
def task():
    """Task management"""
    pass

@task.command("create")
@click.option("--name", "-n", required=True, help="Task name")
@click.option("--description", "-d", default="", help="Task description")
@click.option("--agent-id", "-a", help="Agent ID to assign")
@click.option("--priority", "-p", default=5, type=int, help="Priority 1-10")
@click.option("--max-loops", "-l", default=50, type=int, help="Max loop iterations")
@click.option("--parent", multiple=True, help="Parent task IDs")
@click.option("--context", "-c", type=click.File("r"), help="Context window JSON file")
@pass_config
def task_create(cfg, name, description, agent_id, priority, max_loops, parent, context):
    """Create a new task"""
    client = GuardLoopClient(cfg)
    payload = {
        "name": name,
        "description": description,
        "agent_id": agent_id,
        "priority": priority,
        "max_loops": max_loops,
        "parent_ids": list(parent),
        "context_window": json.load(context) if context else {},
    }
    result = client.post("/tasks", payload)
    print_success(f"Task created: {result['id']}")
    print_json(result)

@task.command("list")
@click.option("--status", "-s", help="Filter by status")
@click.option("--agent-id", "-a", help="Filter by agent")
@click.option("--limit", "-n", default=20, type=int, help="Max results")
@pass_config
def task_list(cfg, status, agent_id, limit):
    """List tasks"""
    client = GuardLoopClient(cfg)
    params = {}
    if status:
        params["status"] = status
    if agent_id:
        params["agent_id"] = agent_id

    result = client.get("/tasks", params)
    tasks = result[:limit]

    if not tasks:
        click.echo("No tasks found.")
        return

    headers = ["ID", "Name", "Status", "Agent", "Priority", "Loop", "Created"]
    rows = []
    for t in tasks:
        rows.append([
            t["id"][:8],
            t["name"][:30],
            t["status"],
            (t.get("agent_id") or "—")[:8],
            str(t["priority"]),
            f"{t['current_loop']}/{t['max_loops']}",
            t["created_at"][:10],
        ])
    print_table(headers, rows)

@task.command("get")
@click.argument("task_id")
@pass_config
def task_get(cfg, task_id):
    """Get task details"""
    client = GuardLoopClient(cfg)
    result = client.get(f"/tasks/{task_id}")
    print_json(result)

@task.command("start")
@click.argument("task_id")
@pass_config
def task_start(cfg, task_id):
    """Start a task"""
    client = GuardLoopClient(cfg)
    result = client.post(f"/tasks/{task_id}/start", {})
    print_success(result.get("status", "started"))

@task.command("score")
@click.argument("task_id")
@pass_config
def task_score(cfg, task_id):
    """Calculate confidence score for a task"""
    client = GuardLoopClient(cfg)
    result = client.post(f"/tasks/{task_id}/score", {})
    print_json(result)

@task.command("graph")
@click.argument("task_id")
@pass_config
def task_graph(cfg, task_id):
    """Show dependency graph for a task"""
    client = GuardLoopClient(cfg)
    result = client.get(f"/tasks/{task_id}/dependency-graph")
    print_json(result)

@task.command("stream")
@click.argument("task_id")
@pass_config
def task_stream(cfg, task_id):
    """Stream real-time events for a task"""
    client = GuardLoopClient(cfg)
    click.echo(f"Connecting to SSE stream for task {task_id}...")
    click.echo("Press Ctrl+C to exit.\n")
    try:
        for event in client.stream_sse(f"/tasks/{task_id}/stream"):
            print_json(event)
    except KeyboardInterrupt:
        click.echo("\nStream closed.")

# ============ AGENTS ============
@cli.group()
def agent():
    """Agent management"""
    pass

@agent.command("list")
@click.option("--type", "-t", help="Filter by agent type")
@pass_config
def agent_list(cfg, type):
    """List registered agents"""
    client = GuardLoopClient(cfg)
    params = {}
    if type:
        params["agent_type"] = type
    result = client.get("/agents", params)

    if not result:
        click.echo("No agents found.")
        return

    headers = ["ID", "Name", "Type", "Status", "Last Seen"]
    rows = []
    for a in result:
        rows.append([
            a["id"][:8],
            a["name"][:25],
            a["agent_type"],
            a["status"],
            a.get("last_seen", "Never")[:10] if a.get("last_seen") else "Never",
        ])
    print_table(headers, rows)

@agent.command("add")
@click.option("--name", "-n", required=True, help="Agent name")
@click.option("--type", "-t", required=True, 
              type=click.Choice(["cursor", "claude_code", "github_copilot", 
                                "openai_codex", "aider", "continue_dev", 
                                "windsurf", "devin", "custom"]),
              help="Agent type")
@click.option("--config", "-c", type=click.File("r"), help="Config JSON file")
@pass_config
def agent_add(cfg, name, type, config):
    """Register a new agent"""
    client = GuardLoopClient(cfg)
    payload = {
        "name": name,
        "agent_type": type,
        "config": json.load(config) if config else {},
    }
    result = client.post("/agents", payload)
    print_success(f"Agent registered: {result['id']}")

@agent.command("delete")
@click.argument("agent_id")
@pass_config
def agent_delete(cfg, agent_id):
    """Remove an agent"""
    client = GuardLoopClient(cfg)
    client.delete(f"/agents/{agent_id}")
    print_success(f"Agent {agent_id} deleted")

# ============ SCORES ============
@cli.group()
def score():
    """Score management"""
    pass

@score.command("list")
@click.option("--task-id", "-t", help="Filter by task")
@click.option("--decision", "-d", type=click.Choice(["auto_approve", "human_review", "block", "pending"]),
              help="Filter by decision")
@pass_config
def score_list(cfg, task_id, decision):
    """List confidence scores"""
    client = GuardLoopClient(cfg)
    params = {}
    if task_id:
        params["task_id"] = task_id
    if decision:
        params["decision"] = decision
    result = client.get("/scores", params)

    if not result:
        click.echo("No scores found.")
        return

    headers = ["ID", "Task", "Overall", "Test", "Coverage", "Security", "Behavior", "Decision"]
    rows = []
    for s in result:
        rows.append([
            s["id"][:8],
            s["task_id"][:8],
            str(s["overall"]),
            str(s["test_score"]),
            str(s["coverage_score"]),
            str(s["security_score"]),
            str(s["behavioral_score"]),
            s["decision"],
        ])
    print_table(headers, rows)

@score.command("override")
@click.argument("score_id")
@click.option("--decision", "-d", required=True,
              type=click.Choice(["auto_approve", "human_review", "block"]),
              help="New decision")
@click.option("--reason", "-r", required=True, help="Override reason")
@pass_config
def score_override(cfg, score_id, decision, reason):
    """Override a score decision"""
    client = GuardLoopClient(cfg)
    result = client.post(f"/scores/{score_id}/override", {
        "decision": decision,
        "reason": reason,
    })
    print_success(f"Score overridden to {decision}")

# ============ PII ============
@cli.group()
def pii():
    """PII and secret scanning"""
    pass

@pii.command("scrub")
@click.argument("file", type=click.File("r"))
@click.option("--task-id", "-t", required=True, help="Task ID to associate scan with")
@click.option("--strict", is_flag=True, help="Strict mode (block on any finding)")
@pass_config
def pii_scrub(cfg, file, task_id, strict):
    """Scan and scrub a file for PII/secrets"""
    client = GuardLoopClient(cfg)
    content = file.read()
    result = client.post("/pii/scrub", {
        "task_id": task_id,
        "context_text": content,
        "strict_mode": strict,
    })

    if result["blocked"]:
        print_error(f"BLOCKED: {result['block_reason']}")
    else:
        print_success(f"Scrubbed. Found {result['findings_count']} PII items, {result['secrets_count']} secrets.")

    if result.get("scrubbed_text"):
        click.echo("\n--- Scrubbed text ---")
        click.echo(result["scrubbed_text"])

@pii.command("scans")
@click.argument("task_id")
@pass_config
def pii_scans(cfg, task_id):
    """Show PII scan history for a task"""
    client = GuardLoopClient(cfg)
    result = client.get(f"/pii/scans/{task_id}")
    print_json(result)

# ============ BROWSER ============
@cli.group()
def browser():
    """Browser verification"""
    pass

@browser.command("verify")
@click.option("--task-id", "-t", required=True, help="Task ID")
@click.option("--url", "-u", required=True, help="URL to verify")
@click.option("--width", default=1280, type=int, help="Viewport width")
@click.option("--height", default=720, type=int, help="Viewport height")
@pass_config
def browser_verify(cfg, task_id, url, width, height):
    """Queue browser verification for a URL"""
    client = GuardLoopClient(cfg)
    result = client.post("/browser/verify", {
        "task_id": task_id,
        "url": url,
        "viewport_width": width,
        "viewport_height": height,
    })
    print_success(result.get("status", "queued"))

@browser.command("list")
@click.argument("task_id")
@pass_config
def browser_list(cfg, task_id):
    """List browser verifications for a task"""
    client = GuardLoopClient(cfg)
    result = client.get(f"/browser/verifications/{task_id}")
    print_json(result)

# ============ MONITOR ============
@cli.command("monitor")
@click.option("--org-id", "-o", default="default-org", help="Organization ID")
@pass_config
def monitor_cmd(cfg, org_id):
    """Connect to live event stream"""
    client = GuardLoopClient(cfg)
    click.echo(f"Connecting to global event stream for org {org_id}...")
    click.echo("Press Ctrl+C to exit.\n")
    try:
        for event in client.stream_sse(f"/sse/org/{org_id}"):
            print_json(event)
    except KeyboardInterrupt:
        click.echo("\nStream closed.")

# ============ CONFIG ============
@cli.command("config")
@pass_config
def config_cmd(cfg):
    """Show current configuration"""
    click.echo(f"Config file: {cfg.config_path}")
    click.echo(f"API URL: {cfg.api_url}")
    click.echo(f"API Key: {'*' * len(cfg.api_key) if cfg.api_key else 'Not set'}")

if __name__ == "__main__":
    cli()
