from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class BrowserVerify(Base):
    __tablename__ = "browser_verifies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)

    url = Column(String(2048), nullable=False)
    viewport = Column(JSON, default={"width": 1280, "height": 720})

    screenshots = Column(JSON, default=list)  # [{path, timestamp, diff_score}]
    a11y_violations = Column(JSON, default=list)
    visual_regression_score = Column(String(50), nullable=True)

    passed = Column(Boolean, default=False)
    failure_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
