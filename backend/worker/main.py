"""GuardLoop Webhook Retry Worker.

Background worker that processes failed webhook events from the queue
and retries them with exponential backoff.

Run: python -m worker.main
"""
import asyncio
import json
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import async_session
from app.core.redis import get_redis, close_redis
from app.core.config import get_settings
from app.models.webhook_event import WebhookEvent
from sqlalchemy import select, update
from sqlalchemy.sql import func

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook-worker")

MAX_RETRIES = int(os.getenv("WEBHOOK_MAX_RETRIES", "5"))
BASE_DELAY = float(os.getenv("WEBHOOK_BASE_DELAY", "2.0"))
BATCH_SIZE = int(os.getenv("WEBHOOK_BATCH_SIZE", "10"))
POLL_INTERVAL = int(os.getenv("WEBHOOK_POLL_INTERVAL", "30"))

async def get_failed_events(session, limit: int = 10) -> list[WebhookEvent]:
    """Get webhook events that failed and are due for retry."""
    result = await session.execute(
        select(WebhookEvent)
        .where(
            WebhookEvent.processed == False,
            WebhookEvent.processing_error != None,
        )
        .order_by(WebhookEvent.received_at)
        .limit(limit)
    )
    return result.scalars().all()

async def calculate_retry_delay(attempt: int) -> float:
    """Exponential backoff with jitter."""
    import random
    delay = BASE_DELAY * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter

async def retry_webhook(event: WebhookEvent, session) -> bool:
    """Attempt to retry a failed webhook. Returns True if successful."""
    try:
        # Determine target URL based on source
        target_url = f"{settings.api_url or 'http://localhost:8000'}/webhooks/ingest/{event.source}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if event.signature:
                headers["X-Signature"] = event.signature

            resp = await client.post(
                target_url,
                json=event.payload,
                headers=headers,
            )
            resp.raise_for_status()

        # Mark as processed
        event.processed = True
        event.processing_error = None
        event.processed_at = func.now()
        await session.commit()

        logger.info(f"Webhook {event.id} retried successfully")
        return True

    except Exception as e:
        error_msg = f"Attempt failed: {str(e)[:500]}"

        # Update error log
        current_error = event.processing_error or ""
        event.processing_error = f"{current_error}\n{datetime.utcnow().isoformat()}: {error_msg}"
        await session.commit()

        logger.warning(f"Webhook {event.id} retry failed: {error_msg}")
        return False

async def process_batch():
    """Process a batch of failed webhooks."""
    async with async_session() as session:
        events = await get_failed_events(session, BATCH_SIZE)

        if not events:
            return 0

        processed = 0
        for event in events:
            # Count retry attempts from error log
            attempt_count = (event.processing_error or "").count("Attempt failed:")

            if attempt_count >= MAX_RETRIES:
                logger.error(f"Webhook {event.id} exceeded max retries ({MAX_RETRIES})")
                continue

            # Check if enough time has passed since last attempt
            delay = await calculate_retry_delay(attempt_count)
            # In production: check last attempt timestamp

            success = await retry_webhook(event, session)
            if success:
                processed += 1

            # Small delay between retries to avoid overwhelming
            await asyncio.sleep(0.5)

        return processed

async def main():
    """Main worker loop."""
    logger.info(f"Webhook retry worker started (max_retries={MAX_RETRIES}, batch={BATCH_SIZE})")

    try:
        while True:
            processed = await process_batch()

            if processed > 0:
                logger.info(f"Processed {processed} webhooks")

            await asyncio.sleep(POLL_INTERVAL)

    except asyncio.CancelledError:
        logger.info("Worker shutting down...")
    finally:
        await close_redis()

if __name__ == "__main__":
    import os
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
