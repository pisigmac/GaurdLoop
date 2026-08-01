"""
Adapter registry: Maps agent types to their adapter implementations.
"""
from typing import Dict, Type
from app.adapters.base import AgentAdapter
from app.adapters.cursor import CursorAdapter
from app.adapters.claude_code import ClaudeCodeAdapter
from app.adapters.github_copilot import GitHubCopilotAdapter
from app.adapters.openai_codex import OpenAICodexAdapter
from app.adapters.aider import AiderAdapter
from app.adapters.continue_dev import ContinueAdapter
from app.adapters.windsurf import WindsurfAdapter
from app.adapters.devin import DevinAdapter

ADAPTER_REGISTRY: Dict[str, Type[AgentAdapter]] = {
    "cursor": CursorAdapter,
    "claude_code": ClaudeCodeAdapter,
    "github_copilot": GitHubCopilotAdapter,
    "openai_codex": OpenAICodexAdapter,
    "aider": AiderAdapter,
    "continue_dev": ContinueAdapter,
    "windsurf": WindsurfAdapter,
    "devin": DevinAdapter,
}

def get_adapter(agent_type: str) -> AgentAdapter:
    if agent_type not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}. Supported: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[agent_type]()

def list_adapters() -> list[str]:
    return list(ADAPTER_REGISTRY.keys())
