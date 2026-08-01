from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskCreate(BaseModel):
    name: str = Field(..., max_length=500)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    parent_ids: List[str] = []
    priority: int = Field(default=5, ge=1, le=10)
    max_loops: int = Field(default=50, ge=1, le=500)
    current_loop: int = 0
    context_size_tokens: int = 0
    context_window: dict = {}
    output: dict = {}
    scheduled_at: Optional[datetime] = None

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    max_loops: Optional[int] = None
    current_loop: Optional[int] = None
    context_size_tokens: Optional[int] = None
    context_window: Optional[dict] = None
    output: Optional[dict] = None

class TaskOut(BaseModel):
    id: str
    org_id: str
    agent_id: Optional[str]
    name: str
    description: Optional[str]
    status: str
    parent_ids: List[str]
    child_ids: List[str]
    priority: int
    max_loops: int
    current_loop: int
    context_size_tokens: int
    output: dict
    error_log: Optional[str]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class TaskDependencyGraph(BaseModel):
    nodes: List[dict]
    edges: List[dict]
    critical_path: List[str]
    estimated_duration_seconds: int
