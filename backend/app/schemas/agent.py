from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class AgentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    agent_type: str = Field(..., pattern="^(cursor|claude_code|github_copilot|openai_codex|aider|continue_dev|windsurf|devin|custom)$")
    config: Dict[str, Any] = {}
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, validation_alias="metadata")

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata")

class AgentOut(BaseModel):
    id: str
    org_id: str
    name: str
    agent_type: str
    config: dict
    status: str
    last_seen: Optional[datetime]
    metadata: dict = Field(default_factory=dict, validation_alias="extra_metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
