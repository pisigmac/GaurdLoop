from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    clerk_user_id = Column(String(255), unique=True, nullable=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    role = Column(String(50), default="member")  # owner, admin, member
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
