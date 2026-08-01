import redis.asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()
_redis_pool = None

async def get_redis():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool

async def close_redis():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
