"""GuardLoop SDK data models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class Decision(str, Enum):
    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    BLOCK = "block"
    PENDING = "pending"

@dataclass
class Task:
    id: str
    org_id: str
    name: str
    status: TaskStatus
    agent_id: Optional[str] = None
    description: Optional[str] = None
    priority: int = 5
    max_loops: int = 50
    current_loop: int = 0
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    context_window: Dict[str, Any] = field(default_factory=dict)
    context_size_tokens: int = 0
    output: Dict[str, Any] = field(default_factory=dict)
    error_log: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            org_id=data["org_id"],
            name=data["name"],
            status=TaskStatus(data.get("status", "pending")),
            agent_id=data.get("agent_id"),
            description=data.get("description"),
            priority=data.get("priority", 5),
            max_loops=data.get("max_loops", 50),
            current_loop=data.get("current_loop", 0),
            parent_ids=data.get("parent_ids", []),
            child_ids=data.get("child_ids", []),
            context_window=data.get("context_window", {}),
            context_size_tokens=data.get("context_size_tokens", 0),
            output=data.get("output", {}),
            error_log=data.get("error_log"),
            created_at=_parse_datetime(data.get("created_at")),
            started_at=_parse_datetime(data.get("started_at")),
            completed_at=_parse_datetime(data.get("completed_at")),
        )

@dataclass
class Agent:
    id: str
    org_id: str
    name: str
    agent_type: str
    status: str
    config: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        return cls(
            id=data["id"],
            org_id=data["org_id"],
            name=data["name"],
            agent_type=data["agent_type"],
            status=data.get("status", "idle"),
            config=data.get("config", {}),
            last_seen=_parse_datetime(data.get("last_seen")),
            metadata=data.get("metadata", {}),
            created_at=_parse_datetime(data.get("created_at")),
        )

@dataclass
class Score:
    id: str
    task_id: str
    org_id: str
    overall: int
    test_score: float
    coverage_score: float
    security_score: float
    behavioral_score: float
    weights: Dict[str, float] = field(default_factory=dict)
    decision: Decision = Decision.PENDING
    test_details: Dict[str, Any] = field(default_factory=dict)
    security_details: Dict[str, Any] = field(default_factory=dict)
    behavioral_details: Dict[str, Any] = field(default_factory=dict)
    override_by: Optional[str] = None
    override_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Score":
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            org_id=data["org_id"],
            overall=data["overall"],
            test_score=data.get("test_score", 0.0),
            coverage_score=data.get("coverage_score", 0.0),
            security_score=data.get("security_score", 0.0),
            behavioral_score=data.get("behavioral_score", 0.0),
            weights=data.get("weights", {}),
            decision=Decision(data.get("decision", "pending")),
            test_details=data.get("test_details", {}),
            security_details=data.get("security_details", {}),
            behavioral_details=data.get("behavioral_details", {}),
            override_by=data.get("override_by"),
            override_reason=data.get("override_reason"),
            created_at=_parse_datetime(data.get("created_at")),
        )

    @property
    def passed(self) -> bool:
        return self.decision == Decision.AUTO_APPROVE

    @property
    def needs_review(self) -> bool:
        return self.decision == Decision.HUMAN_REVIEW

    @property
    def blocked(self) -> bool:
        return self.decision == Decision.BLOCK

@dataclass
class PiiScan:
    id: str
    task_id: str
    raw_context_hash: str
    scrubbed_context_hash: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    secrets_found: List[Dict[str, Any]] = field(default_factory=list)
    blocked: bool = False
    block_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PiiScan":
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            raw_context_hash=data["raw_context_hash"],
            scrubbed_context_hash=data["scrubbed_context_hash"],
            findings=data.get("findings", []),
            secrets_found=data.get("secrets_found", []),
            blocked=data.get("blocked", False),
            block_reason=data.get("block_reason"),
            created_at=_parse_datetime(data.get("created_at")),
        )

@dataclass
class BrowserVerify:
    id: str
    task_id: str
    url: str
    passed: bool = False
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1280, "height": 720})
    screenshots: List[Dict[str, Any]] = field(default_factory=list)
    a11y_violations: List[Dict[str, Any]] = field(default_factory=list)
    visual_regression_score: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "BrowserVerify":
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            url=data["url"],
            passed=data.get("passed", False),
            viewport=data.get("viewport", {"width": 1280, "height": 720}),
            screenshots=data.get("screenshots", []),
            a11y_violations=data.get("a11y_violations", []),
            visual_regression_score=data.get("visual_regression_score"),
            failure_reason=data.get("failure_reason"),
            created_at=_parse_datetime(data.get("created_at")),
        )

def _parse_datetime(value) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try ISO format
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None
