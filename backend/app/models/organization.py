from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Float
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    clerk_org_id = Column(String(255), unique=True, nullable=True)
    settings = Column(JSON, default=dict)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
