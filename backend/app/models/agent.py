from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, Integer
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)  # cursor, claude_code, github_copilot, custom
    config = Column(JSON, default=dict)  # api keys, endpoints, model settings
    status = Column(String(50), default="idle")  # idle, running, error, paused
    last_seen = Column(DateTime(timezone=True), nullable=True)
    extra_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
