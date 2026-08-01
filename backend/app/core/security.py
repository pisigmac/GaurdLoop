try:
    from jose import jwt, ExpiredSignatureError
except ImportError:
    import jwt
    from jwt import ExpiredSignatureError

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.core.config import get_settings
import json
from functools import lru_cache

settings = get_settings()
security = HTTPBearer(auto_error=False)

@lru_cache()
def _get_clerk_jwks():
    # In production, fetch from Clerk JWKS endpoint
    # For now, return a mock structure
    return {"keys": []}

async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = credentials.credentials
    try:
        # In production: fetch JWKS, verify signature, check exp
        # Simplified for scaffold:
        payload = jwt.decode(
            token,
            key="",
            options={"verify_signature": False, "verify_exp": True},
            algorithms=["RS256"]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def require_auth():
    return verify_clerk_token
