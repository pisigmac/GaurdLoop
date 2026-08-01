# GuardLoop Webhook Bridge

A lightweight relay service that receives webhooks from AI agents and forwards them to GuardLoop with authentication, retries, and payload transformation.

## Why Use This?

- **Firewall/NAT**: Your agents can't reach GuardLoop directly
- **Payload transformation**: Convert GitHub/Slack/Cursor payloads to GuardLoop format
- **Batching/buffering**: Queue webhooks during GuardLoop downtime
- **Custom filtering**: Drop or modify events before forwarding
- **Audit trail**: Log all received webhooks for compliance

## Install

```bash
cd bridge
pip install -e .
# or
uvicorn guardloop_bridge.main:app --host 0.0.0.0 --port 8001
```

## Configure

```bash
export GUARDLOOP_API_URL="http://localhost:8000"
export GUARDLOOP_API_KEY="your-api-key"
export BRIDGE_WEBHOOK_SECRET="shared-secret-for-verification"
export BRIDGE_MAX_RETRIES="3"
export BRIDGE_RETRY_DELAY="2.0"
```

## Endpoints

| Endpoint | Description |
|---|---|
| `POST /webhook/{source}` | Generic webhook receiver (any source) |
| `POST /webhook/github` | GitHub webhooks with PR transformation |
| `POST /webhook/slack` | Slack event callbacks with URL verification |
| `POST /webhook/cursor` | Cursor automation webhooks |
| `GET /health` | Health check |
| `GET /events` | Recent received events (debug) |

## Docker

```bash
docker build -t guardloop-bridge .
docker run -p 8001:8001 -e GUARDLOOP_API_URL=http://host.docker.internal:8000 guardloop-bridge
```

## GitHub Webhook Setup

1. Go to your repo Settings -> Webhooks
2. Payload URL: `https://your-bridge.com/webhook/github`
3. Content type: `application/json`
4. Secret: your `BRIDGE_WEBHOOK_SECRET`
5. Events: Pull requests, Pushes, Issues

## Slack Event Setup

1. Create a Slack app
2. Enable Event Subscriptions
3. Request URL: `https://your-bridge.com/webhook/slack`
4. Subscribe to bot events: `message.channels`
