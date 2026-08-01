from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    action = Column(String(100), nullable=False)  # task_created, score_calculated, pii_blocked, etc.
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)

    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
