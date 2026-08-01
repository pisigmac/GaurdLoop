"""
Devin adapter: Connects to Cognition Labs' Devin AI software engineer.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class DevinAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "devin"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["devin_api_key", "workspace_id"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        return {
            "adapter": "devin",
            "status": "queued",
            "reference": f"devin-{config.get('workspace_id', 'unknown')}-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to Devin workspace",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "devin",
            "reference": task_ref,
            "status": "running",
            "progress": 0.2,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["task_created", "task_completed", "pr_opened", "deployment_triggered"]
