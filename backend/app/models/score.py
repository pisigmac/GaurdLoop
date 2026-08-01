from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Score(Base):
    __tablename__ = "scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)

    overall = Column(Integer, nullable=False)  # 0-100

    # Components
    test_score = Column(Float, default=0.0)
    coverage_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)

    # Weights used
    weights = Column(JSON, default=dict)

    # Details
    test_details = Column(JSON, default=dict)
    security_details = Column(JSON, default=dict)
    behavioral_details = Column(JSON, default=dict)

    # Decision
    decision = Column(String(50), default="pending")  # auto_approve, human_review, block
    override_by = Column(String(36), nullable=True)
    override_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
