"""Webhook bridge server.

A lightweight FastAPI service that receives webhooks from agents (Cursor, GitHub, etc.)
and forwards them to the GuardLoop API with proper authentication and retry logic.

This is useful when:
- Your agent can't reach GuardLoop directly (firewall, NAT)
- You need to transform webhook payloads before sending
- You want to batch or buffer webhooks
- You need custom filtering or routing logic
"""
import os
import json
import hmac
import hashlib
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="GuardLoop Webhook Bridge", version="1.0.0")

# Configuration
GUARDLOOP_API_URL = os.getenv("GUARDLOOP_API_URL", "http://localhost:8000")
GUARDLOOP_API_KEY = os.getenv("GUARDLOOP_API_KEY", "")
WEBHOOK_SECRET = os.getenv("BRIDGE_WEBHOOK_SECRET", "")
MAX_RETRIES = int(os.getenv("BRIDGE_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("BRIDGE_RETRY_DELAY", "2.0"))

# In-memory store for recent events (use Redis in production)
event_log: list[Dict[str, Any]] = []

async def forward_to_guardloop(source: str, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
    """Forward a webhook to the GuardLoop API with retries."""
    url = f"{GUARDLOOP_API_URL}/webhooks/ingest/{source}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if GUARDLOOP_API_KEY:
        headers["Authorization"] = f"Bearer {GUARDLOOP_API_KEY}"
    if signature:
        headers["X-Signature"] = signature

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))

    raise HTTPException(status_code=502, detail=f"Failed to forward webhook after {MAX_RETRIES} attempts: {last_error}")

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 webhook signature."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.post("/webhook/{source}")
async def receive_webhook(
    source: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: Optional[str] = Header(None),
    x_event_type: Optional[str] = Header(None),
):
    """Receive a webhook from an agent and forward to GuardLoop."""
    body = await request.body()
    payload = json.loads(body)

    # Verify signature if configured
    if WEBHOOK_SECRET and x_signature:
        if not verify_signature(body, x_signature, WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Add event type from header if not in payload
    if x_event_type and "event_type" not in payload:
        payload["event_type"] = x_event_type

    # Log event
    event = {
        "received_at": datetime.utcnow().isoformat(),
        "source": source,
        "payload": payload,
        "signature": x_signature,
        "status": "forwarding",
    }
    event_log.append(event)

    # Forward in background
    async def do_forward():
        try:
            result = await forward_to_guardloop(source, payload, x_signature)
            event["status"] = "delivered"
            event["guardloop_response"] = result
        except Exception as e:
            event["status"] = "failed"
            event["error"] = str(e)

    background_tasks.add_task(do_forward)

    return {"received": True, "source": source, "forwarding": True}

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "guardloop-bridge", "guardloop_api": GUARDLOOP_API_URL}

@app.get("/events")
async def list_events(limit: int = 50):
    """List recent received events (for debugging)."""
    return event_log[-limit:][::-1]

@app.get("/events/{event_id}")
async def get_event(event_id: int):
    """Get a specific event by index."""
    if event_id < 0 or event_id >= len(event_log):
        raise HTTPException(status_code=404, detail="Event not found")
    return event_log[event_id]

# Source-specific endpoints with payload transformation

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
):
    """Receive GitHub webhooks with automatic payload transformation."""
    body = await request.body()
    payload = json.loads(body)

    # Transform GitHub payload to GuardLoop format
    guardloop_payload = {
        "event_type": x_github_event or "unknown",
        "repository": payload.get("repository", {}).get("full_name"),
        "sender": payload.get("sender", {}).get("login"),
        "payload": payload,
    }

    # Add PR-specific fields
    if "pull_request" in payload:
        guardloop_payload["pr_number"] = payload["pull_request"]["number"]
        guardloop_payload["pr_title"] = payload["pull_request"]["title"]
        guardloop_payload["pr_state"] = payload["pull_request"]["state"]

    event = {
        "received_at": datetime.utcnow().isoformat(),
        "source": "github",
        "payload": guardloop_payload,
        "status": "forwarding",
    }
    event_log.append(event)

    async def do_forward():
        try:
            result = await forward_to_guardloop("github", guardloop_payload, x_hub_signature_256)
            event["status"] = "delivered"
            event["guardloop_response"] = result
        except Exception as e:
            event["status"] = "failed"
            event["error"] = str(e)

    background_tasks.add_task(do_forward)
    return {"received": True, "source": "github", "event": x_github_event}

@app.post("/webhook/slack")
async def slack_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive Slack event callbacks."""
    payload = await request.json()

    # Handle Slack URL verification
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # Transform Slack payload
    guardloop_payload = {
        "event_type": payload.get("event", {}).get("type", "message"),
        "channel": payload.get("event", {}).get("channel"),
        "user": payload.get("event", {}).get("user"),
        "text": payload.get("event", {}).get("text"),
        "payload": payload,
    }

    event = {
        "received_at": datetime.utcnow().isoformat(),
        "source": "slack",
        "payload": guardloop_payload,
        "status": "forwarding",
    }
    event_log.append(event)

    async def do_forward():
        try:
            result = await forward_to_guardloop("slack", guardloop_payload)
            event["status"] = "delivered"
            event["guardloop_response"] = result
        except Exception as e:
            event["status"] = "failed"
            event["error"] = str(e)

    background_tasks.add_task(do_forward)
    return {"received": True, "source": "slack"}

@app.post("/webhook/cursor")
async def cursor_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_cursor_signature: Optional[str] = Header(None),
):
    """Receive Cursor automation webhooks."""
    body = await request.body()
    payload = json.loads(body)

    event = {
        "received_at": datetime.utcnow().isoformat(),
        "source": "cursor",
        "payload": payload,
        "status": "forwarding",
    }
    event_log.append(event)

    async def do_forward():
        try:
            result = await forward_to_guardloop("cursor", payload, x_cursor_signature)
            event["status"] = "delivered"
            event["guardloop_response"] = result
        except Exception as e:
            event["status"] = "failed"
            event["error"] = str(e)

    background_tasks.add_task(do_forward)
    return {"received": True, "source": "cursor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
