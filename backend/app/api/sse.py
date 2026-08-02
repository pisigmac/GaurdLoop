from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from app.core.redis import get_redis

router = APIRouter(prefix="/sse", tags=["sse"])

@router.get("/org/{org_id}")
async def org_events(org_id: str):
    async def event_generator():
        redis = await get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"guardloop:org:{org_id}")

        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'org_id': org_id})}\n\n"

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    raw_payload = message.get("data", {})
                    if isinstance(raw_payload, str):
                        try:
                            parsed_payload = json.loads(raw_payload)
                        except Exception:
                            parsed_payload = raw_payload
                    else:
                        parsed_payload = raw_payload

                    event_data = {
                        "type": "org_event",
                        "payload": parsed_payload,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                await asyncio.sleep(0.5)
        finally:
            await pubsub.unsubscribe(f"guardloop:org:{org_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.get("/global")
async def global_events():
    async def event_generator():
        redis = await get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe("guardloop:global")

        yield f"data: {json.dumps({'type': 'connected', 'scope': 'global'})}\n\n"

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    raw_payload = message.get("data", {})
                    if isinstance(raw_payload, str):
                        try:
                            parsed_payload = json.loads(raw_payload)
                        except Exception:
                            parsed_payload = raw_payload
                    else:
                        parsed_payload = raw_payload

                    event_data = {
                        "type": "global_event",
                        "payload": parsed_payload,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                await asyncio.sleep(0.5)
        finally:
            await pubsub.unsubscribe("guardloop:global")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
