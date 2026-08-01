"""Rate limiting middleware using Redis token bucket.

Tiers:
- Free: 60 req/min
- Pro: 600 req/min
- Enterprise: 6000 req/min
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from typing import Optional

from app.core.redis import get_redis
from app.core.config import get_settings

settings = get_settings()

# Tier limits (requests per minute)
TIER_LIMITS = {
    "free": 60,
    "pro": 600,
    "enterprise": 6000,
}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if request.method == "OPTIONS" or settings.ENV == "development" or path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # Get client identifier (API key or IP)
        client_id = await self._get_client_id(request)
        if not client_id:
            return await call_next(request)

        # Get tier (in production: lookup from org settings)
        tier = await self._get_tier(client_id)
        limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

        # Check rate limit
        allowed, remaining, reset_time = await self._check_rate_limit(client_id, limit)

        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": int(reset_time - time.time()),
                    "limit": limit,
                    "tier": tier,
                },
            )
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(reset_time))
            response.headers["Retry-After"] = str(int(reset_time - time.time()))
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response

    async def _get_client_id(self, request: Request) -> Optional[str]:
        """Extract client identifier from API key or IP."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            key = auth[7:]
            # Use key prefix as identifier
            return f"apikey:{key[:8]}"

        # Fallback to IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client = request.client
        if client:
            return f"ip:{client.host}"

        return None

    async def _get_tier(self, client_id: str) -> str:
        """Get tier for client. In production: lookup from DB."""
        # Default to free for now
        return "free"

    async def _check_rate_limit(self, client_id: str, limit: int) -> tuple[bool, int, float]:
        """Token bucket rate limit check. Returns (allowed, remaining, reset_time)."""
        try:
            redis = await get_redis()
            key = f"ratelimit:{client_id}"
            window = 60  # 1 minute window

            pipe = redis.pipeline()
            pipe.multi()

            # Get current count and TTL
            pipe.get(key)
            pipe.ttl(key)

            results = await pipe.execute()
            current_count = int(results[0] or 0)
            ttl = int(results[1] or 0)

            now = time.time()

            if ttl <= 0:
                # New window
                await redis.setex(key, window, 1)
                return True, limit - 1, now + window

            if current_count >= limit:
                return False, 0, now + ttl

            # Increment count
            await redis.incr(key)
            remaining = limit - current_count - 1

            return True, max(0, remaining), now + ttl

        except Exception:
            # If Redis is down, allow the request (fail open)
            return True, limit, time.time() + 60
