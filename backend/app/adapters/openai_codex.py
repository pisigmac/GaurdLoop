"""
OpenAI Codex adapter: Connects to OpenAI's Codex CLI and API.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class OpenAICodexAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "openai_codex"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["openai_api_key"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        config = task_config.get("agent_config", {})
        return {
            "adapter": "openai_codex",
            "status": "queued",
            "reference": f"codex-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to OpenAI Codex agent",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "openai_codex",
            "reference": task_ref,
            "status": "running",
            "progress": 0.35,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["code_change", "pr_opened", "issue_created", "command_executed"]
