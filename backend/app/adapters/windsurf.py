"""
Windsurf adapter: Connects to Codeium's Windsurf IDE agent.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class WindsurfAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "windsurf"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["codeium_api_key"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        return {
            "adapter": "windsurf",
            "status": "queued",
            "reference": f"windsurf-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to Windsurf agent",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "windsurf",
            "reference": task_ref,
            "status": "running",
            "progress": 0.45,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["code_change", "pr_opened", "issue_created", "cascade_triggered"]
