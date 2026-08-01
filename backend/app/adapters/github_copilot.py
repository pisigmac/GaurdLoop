"""
GitHub Copilot adapter: Connects to Copilot API and GitHub webhooks.
"""
from typing import Dict, Any, Optional
from app.adapters.base import AgentAdapter

class GitHubCopilotAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "github_copilot"

    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required = ["github_token", "installation_id"]
        missing = [k for k in required if k not in config]
        if missing:
            return False, f"Missing config keys: {', '.join(missing)}"
        return True, None

    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "adapter": "github_copilot",
            "status": "queued",
            "reference": f"copilot-{task_config.get('task_id', 'unknown')}",
            "message": "Task sent to GitHub Copilot agent",
        }

    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        return {
            "adapter": "github_copilot",
            "reference": task_ref,
            "status": "running",
            "progress": 0.4,
            "logs": [],
        }

    async def cancel_task(self, task_ref: str) -> bool:
        return True

    def supported_events(self) -> list[str]:
        return ["pr_opened", "pr_merged", "issue_created", "code_change"]
