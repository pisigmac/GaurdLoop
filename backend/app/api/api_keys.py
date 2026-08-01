from fastapi import APIRouter, Depends, HTTPException, Security, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.core.config import get_settings
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyOut, ApiKeyCreateResponse, ApiKeyUsage
from app.core.security import security

router = APIRouter(prefix="/api-keys", tags=["api-keys"])
settings = get_settings()

async def get_api_key(request: Request, db: AsyncSession = Depends(get_db)):
    """Extract and validate API key from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    key = auth[7:]
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.revoked == False
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")

    # Update last used
    await db.execute(
        update(ApiKey).where(ApiKey.id == api_key.id).values(last_used_at=datetime.utcnow())
    )
    await db.commit()

    return api_key

@router.post("", response_model=ApiKeyCreateResponse)
async def create_api_key(data: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new API key. The full key is returned only once."""
    full_key, key_hash, prefix = ApiKey.generate_key()

    api_key = ApiKey(
        org_id="default-org",
        name=data.name,
        key_hash=key_hash,
        key_prefix=prefix,
        scopes=data.scopes,
        expires_at=data.expires_at,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": api_key.id,
        "org_id": api_key.org_id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "last_used_at": api_key.last_used_at,
        "expires_at": api_key.expires_at,
        "revoked": api_key.revoked,
        "created_at": api_key.created_at,
        "full_key": full_key,
    }

@router.get("", response_model=List[ApiKeyOut])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    """List all API keys for the organization."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.org_id == "default-org").order_by(ApiKey.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{key_id}", response_model=ApiKeyOut)
async def get_api_key_detail(key_id: str, db: AsyncSession = Depends(get_db)):
    """Get API key details."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == "default-org")
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key

@router.post("/{key_id}/revoke")
async def revoke_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    """Revoke an API key."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == "default-org")
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    key.revoked = True
    await db.commit()
    return {"revoked": True}

@router.get("/{key_id}/usage", response_model=ApiKeyUsage)
async def get_api_key_usage(key_id: str, db: AsyncSession = Depends(get_db)):
    """Get usage statistics for an API key."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == "default-org")
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    # In production: query from Redis or analytics DB
    return {
        "total_requests": 0,
        "last_used": key.last_used_at,
        "endpoints": {},
    }
