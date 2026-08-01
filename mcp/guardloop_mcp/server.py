"""MCP Server implementation for GuardLoop.

This server exposes GuardLoop capabilities as MCP tools that any MCP client
(Cursor, Claude Desktop, Claude Code, etc.) can call directly.

Tools:
- guardloop_score_task: Calculate confidence score for a task
- guardloop_scrub_context: Scan and scrub text for PII/secrets
- guardloop_verify_browser: Queue browser verification for a URL
- guardloop_get_task_status: Get current task status and loop state
- guardloop_list_agents: List registered agents
- guardloop_create_task: Create a new task with dependencies
- guardloop_override_score: Override a score decision (admin only)
"""
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from guardloop_mcp.client import GuardLoopMCPClient

# Initialize server
server = Server("guardloop")
client = GuardLoopMCPClient(
    api_key=os.getenv("GUARDLOOP_API_KEY", ""),
    base_url=os.getenv("GUARDLOOP_API_URL", "http://localhost:8000"),
)

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="guardloop_score_task",
            description="Calculate a 0-100 confidence score for an agent task. Returns test, coverage, security, and behavioral scores with a gate decision (auto_approve, human_review, or block).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID to score"},
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="guardloop_scrub_context",
            description="Scan text for PII and secrets before sending to an LLM. Returns scrubbed text, findings count, and whether the context was blocked.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to associate the scan with"},
                    "context_text": {"type": "string", "description": "The text to scan for PII and secrets"},
                    "strict_mode": {"type": "boolean", "description": "If true, block on any finding", "default": False},
                },
                "required": ["task_id", "context_text"],
            },
        ),
        Tool(
            name="guardloop_verify_browser",
            description="Queue a headless browser verification for a URL. Checks accessibility violations and visual regression against a baseline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to associate verification with"},
                    "url": {"type": "string", "description": "URL to verify"},
                    "viewport_width": {"type": "integer", "default": 1280},
                    "viewport_height": {"type": "integer", "default": 720},
                },
                "required": ["task_id", "url"],
            },
        ),
        Tool(
            name="guardloop_get_task_status",
            description="Get the current status of a task including loop count, context size, and any errors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID to check"},
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="guardloop_list_agents",
            description="List all registered agents in the organization with their status and type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_type": {"type": "string", "description": "Filter by agent type (cursor, claude_code, etc.)"},
                },
            },
        ),
        Tool(
            name="guardloop_create_task",
            description="Create a new task in GuardLoop. The task will be queued and can depend on other tasks completing first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Task name"},
                    "description": {"type": "string", "description": "Task description"},
                    "agent_id": {"type": "string", "description": "Agent ID to assign"},
                    "priority": {"type": "integer", "description": "Priority 1-10", "default": 5},
                    "max_loops": {"type": "integer", "description": "Max loop iterations", "default": 50},
                    "parent_ids": {"type": "array", "items": {"type": "string"}, "description": "Task IDs this depends on"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="guardloop_override_score",
            description="Override a score decision. Use with caution — this bypasses the automated gate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "score_id": {"type": "string", "description": "Score ID to override"},
                    "decision": {"type": "string", "enum": ["auto_approve", "human_review", "block"], "description": "New decision"},
                    "reason": {"type": "string", "description": "Reason for override"},
                },
                "required": ["score_id", "decision", "reason"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    try:
        if name == "guardloop_score_task":
            result = client.score_task(arguments["task_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_scrub_context":
            result = client.scrub_context(
                task_id=arguments["task_id"],
                context_text=arguments["context_text"],
                strict_mode=arguments.get("strict_mode", False),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_verify_browser":
            result = client.verify_browser(
                task_id=arguments["task_id"],
                url=arguments["url"],
                viewport_width=arguments.get("viewport_width", 1280),
                viewport_height=arguments.get("viewport_height", 720),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_get_task_status":
            result = client.get_task(arguments["task_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_list_agents":
            result = client.list_agents(agent_type=arguments.get("agent_type"))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_create_task":
            result = client.create_task(
                name=arguments["name"],
                description=arguments.get("description", ""),
                agent_id=arguments.get("agent_id"),
                priority=arguments.get("priority", 5),
                max_loops=arguments.get("max_loops", 50),
                parent_ids=arguments.get("parent_ids", []),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "guardloop_override_score":
            result = client.override_score(
                score_id=arguments["score_id"],
                decision=arguments["decision"],
                reason=arguments["reason"],
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
