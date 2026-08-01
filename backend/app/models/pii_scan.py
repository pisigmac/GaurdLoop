from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class PiiScan(Base):
    __tablename__ = "pii_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)

    raw_context_hash = Column(String(64), nullable=False)
    scrubbed_context_hash = Column(String(64), nullable=False)

    findings = Column(JSON, default=list)  # [{type, start, end, confidence, replacement}]
    secrets_found = Column(JSON, default=list)

    blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
