from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str
    scopes: str = "read,write"
    expires_at: Optional[datetime] = None

class ApiKeyOut(BaseModel):
    id: str
    org_id: str
    name: str
    key_prefix: str
    scopes: str
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(ApiKeyOut):
    full_key: str  # Only returned once on creation

class ApiKeyUsage(BaseModel):
    total_requests: int
    last_used: Optional[datetime]
    endpoints: dict
