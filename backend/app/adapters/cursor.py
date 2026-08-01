"""
Cursor adapter: Connects to Cursor Automations via webhooks and MCP.
"""
import httpx
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class CursorAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "cursor"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["api_key", "team_id"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        api_key = config.get("api_key")
        team_id = config.get("team_id")

        # In production: call Cursor API or trigger automation
        # For now, return a mock reference
        return {
            "adapter": "cursor",
            "status": "queued",
            "reference": f"cursor-{team_id}-{task_config.get('task_id', 'unknown')}",
            "message": "Task queued in Cursor cloud sandbox",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        # In production: poll Cursor API
        return {
            "adapter": "cursor",
            "reference": task_ref,
            "status": "running",  # or completed, failed
            "progress": 0.5,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        # In production: call Cursor API to cancel
        return True

    def supported_events(self) -> list[str]:
        return [
            "pr_opened",
            "pr_merged",
            "issue_created",
            "automation_triggered",
            "code_change",
        ]
