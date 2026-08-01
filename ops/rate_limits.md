# Rate Limits

## Tiers

| Tier | Requests/min | Tasks/month | Browser runs/month |
|---|---|---|---|
| Free | 60 | 50 | 10 |
| Pro | 600 | 500 | 200 |
| Enterprise | 6000 | Unlimited | Unlimited |

## Implementation

Redis-backed token bucket per API key / org ID.

```python
# Middleware pseudocode
async def rate_limit(request):
    key = f"rate_limit:{org_id}"
    current = await redis.get(key) or 0
    if current >= limit:
        raise HTTPException(429, "Rate limit exceeded")
    await redis.incr(key)
    await redis.expire(key, 60)
```

## Headers

- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Remaining
- `X-RateLimit-Reset`: Unix timestamp
