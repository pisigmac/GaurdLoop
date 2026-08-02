from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import hmac
import hashlib
import json
from app.core.database import get_db
from app.core.config import get_settings
from app.core.redis import broadcast_event
from app.models.webhook_event import WebhookEvent
from app.models.task import Task
from app.schemas.webhook import WebhookIngest, WebhookOut
from app.services.taskgraph import TaskGraphEngine

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()

@router.post("/ingest/{source}")
async def ingest_webhook(
    source: str,
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()

    # Verify signature if configured
    if x_signature and settings.WEBHOOK_SECRET:
        expected = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(f"sha256={expected}", x_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    event = WebhookEvent(
        org_id="default-org",
        source=source,
        event_type=payload.get("event_type", "unknown"),
        payload=payload,
        signature=x_signature,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    await broadcast_event("default-org", "webhook_ingested", {
        "source": source,
        "event_type": payload.get("event_type", "unknown"),
        "event_id": str(event.id)
    })

    # Auto-create task for certain events
    if source in ["cursor", "github"] and payload.get("event_type") in ["pr_opened", "code_change", "automation_triggered"]:
        task = Task(
            org_id="default-org",
            name=f"Auto: {payload.get('event_type')} from {source}",
            description=json.dumps(payload)[:1000],
            status="pending",
            priority=5,
            context_window={"webhook_payload": payload, "source": source},
        )
        db.add(task)
        await db.commit()

        event.task_id = task.id
        event.processed = True
        event.processed_at = func.now()
        await db.commit()

    return {"received": True, "event_id": event.id, "task_id": event.task_id}

@router.get("", response_model=List[WebhookOut])
async def list_webhooks(
    source: str = None,
    processed: bool = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(WebhookEvent).where(WebhookEvent.org_id == "default-org")
    if source:
        query = query.where(WebhookEvent.source == source)
    if processed is not None:
        query = query.where(WebhookEvent.processed == processed)
    query = query.order_by(WebhookEvent.received_at.desc())

    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{event_id}/retry")
async def retry_webhook(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WebhookEvent).where(WebhookEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.processed = False
    event.processing_error = None
    await db.commit()

    return {"status": "queued_for_retry", "event_id": event_id}
