from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, Integer, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True, index=True)

    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, queued, running, completed, failed, blocked

    # Dependency graph
    parent_ids = Column(JSON, default=list)  # list of task IDs this depends on
    child_ids = Column(JSON, default=list)

    # Execution
    priority = Column(Integer, default=5)  # 1-10
    max_loops = Column(Integer, default=50)
    current_loop = Column(Integer, default=0)

    # Context
    context_window = Column(JSON, default=dict)  # files, prompts, history
    context_size_tokens = Column(Integer, default=0)

    # Results
    output = Column(JSON, default=dict)
    error_log = Column(Text, nullable=True)

    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
