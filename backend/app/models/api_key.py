from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import secrets

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    name = Column(String(255), nullable=False)
    key_hash = Column(String(64), nullable=False, index=True)
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for display

    scopes = Column(Text, default="read,write")  # comma-separated
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def generate_key():
        """Generate a new API key. Returns (full_key, hash, prefix)."""
        full = "gl_" + secrets.token_urlsafe(32)
        prefix = full[:8]
        import hashlib
        key_hash = hashlib.sha256(full.encode()).hexdigest()
        return full, key_hash, prefix
