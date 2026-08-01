"""
Base adapter interface for multi-agent support.
All agent adapters must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AgentAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task to the agent and return a reference."""
        pass

    @abstractmethod
    async def get_status(self, task_ref: str) -> Dict[str, Any]:
        """Poll or receive status update for a running task."""
        pass

    @abstractmethod
    async def cancel_task(self, task_ref: str) -> bool:
        """Cancel a running task."""
        pass

    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate adapter-specific configuration."""
        pass

    @abstractmethod
    def supported_events(self) -> list[str]:
        """Return list of webhook event types this adapter handles."""
        pass
