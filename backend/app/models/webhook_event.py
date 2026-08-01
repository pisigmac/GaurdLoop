from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)

    source = Column(String(100), nullable=False)  # cursor, github, slack, linear, pagerduty
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    signature = Column(String(255), nullable=True)

    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True)

    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
