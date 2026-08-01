"""
Claude Code adapter: Connects to Claude Code CLI or API.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class ClaudeCodeAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "claude_code"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["anthropic_api_key"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        return {
            "adapter": "claude_code",
            "status": "queued",
            "reference": f"claude-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to Claude Code agent",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "claude_code",
            "reference": task_ref,
            "status": "running",
            "progress": 0.3,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["code_change", "pr_opened", "issue_created"]
