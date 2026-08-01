"""
Continue.dev adapter: Connects to Continue IDE extension.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class ContinueAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "continue_dev"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["server_url"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        return {
            "adapter": "continue_dev",
            "status": "queued",
            "reference": f"continue-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to Continue.dev agent",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "continue_dev",
            "reference": task_ref,
            "status": "running",
            "progress": 0.25,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["code_change", "context_loaded", "command_executed"]
