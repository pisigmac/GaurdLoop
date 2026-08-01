# Agent Adapter Development

## Adding a New Agent

1. Create `backend/app/adapters/your_agent.py`
2. Implement `AgentAdapter` base class
3. Register in `backend/app/adapters/registry.py`

```python
from app.adapters.base import AgentAdapter

class YourAgentAdapter(AgentAdapter):
    @property
    def name(self) -> str:
        return "your_agent"

    async def send_task(self, task_config: dict) -> dict:
        # Call agent API
        pass

    async def get_status(self, task_ref: str) -> dict:
        # Poll or receive status
        pass

    async def cancel_task(self, task_ref: str) -> bool:
        pass

    async def validate_config(self, config: dict) -> tuple[bool, str | None]:
        pass

    def supported_events(self) -> list[str]:
        return ["code_change", "pr_opened"]
```

## Event Mapping

Each adapter declares which webhook events it handles. GuardLoop routes incoming webhooks to the correct adapter based on source + event_type.
