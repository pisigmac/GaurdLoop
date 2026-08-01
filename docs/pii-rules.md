# Dynamic PII & Secret Detection Rules

GuardLoop provides a zero-latency, real-time sanitization engine (`ContextScrub`) that prevents sensitive credentials, personal identifiable information (PII), and proprietary tokens from leaking to third-party Large Language Models (LLMs).

PII and secret detection rules in GuardLoop can be **dynamically created, edited, and toggled at runtime** without requiring codebase changes or server restarts.

---

## 🏗️ Architecture & High-Availability Sync

GuardLoop uses a hybrid database-and-cache architecture to ensure dynamic rule updates take effect instantly with **0ms runtime overhead** during agent execution:

```text
┌──────────────────────────┐       ┌────────────────────────┐       ┌─────────────────────────┐
│ Admin UI / REST API      │ ────> │ PostgreSQL (pii_rules) │ ────> │ Redis Pub/Sub Cache Sync│
│ (Create/Update Rule)     │       │ (Rule Database)        │       │ (Real-Time Broadcast)   │
└──────────────────────────┘       └────────────────────────┘       └────────────┬────────────┘
                                                                                 │
                                                                                 ▼
                                                                    ┌─────────────────────────┐
                                                                    │ Real-Time ContextScrub  │
                                                                    │ (In-Memory Regex Sync)  │
                                                                    └─────────────────────────┘
```

1. **Database Storage**: Rules are persisted in PostgreSQL (`pii_rules` table), scoped by organization ID.
2. **In-Memory Worker Sync**: When a rule is modified, a Redis Pub/Sub event notifies all running GuardLoop API instances.
3. **0ms In-Memory Interception**: Regex patterns are pre-compiled and evaluated in-memory before prompt payloads are dispatched to model providers.

---

## 🛠️ Step-by-Step Configuration Guide

### Step 1: Open PII Governance Settings
Access the PII rules management panel:
- **Web UI**: Navigate to `http://localhost:33000/settings` or the **PII Rules** tab in the GuardLoop Dashboard.
- **API**: Use the `/api/v1/pii-rules` REST endpoint.

### Step 2: Define Rule Metadata & Scope
Click **Add PII Rule** and specify the basic configuration:

| Field | Description | Example |
| :--- | :--- | :--- |
| **Rule Name** | Human-readable identifier for the rule. | `Stripe Live Secret Key` |
| **Category** | Classification (`secret`, `pii`, `financial`, `health`). | `secret` |
| **Status** | State (`active`, `disabled`). | `active` |

### Step 3: Configure Detection Pattern
Select the matching strategy:

- **Regex Pattern**: Custom regular expression targeting specific enterprise formats.
  - *Example Employee ID*: `EMP-[0-9]{6}`
  - *Example Internal Auth Token*: `bearer_gl_live_[a-zA-Z0-9]{32}`
- **Presidio Entity**: Pre-built AI entity detectors (`CREDIT_CARD`, `US_SSN`, `EMAIL_ADDRESS`, `IP_ADDRESS`, `PHONE_NUMBER`).

### Step 4: Select Enforcement Action

| Action | Behavior |
| :--- | :--- |
| **Redact / Mask (Default)** | Inline replacement of sensitive data with a token (e.g., `[REDACTED_STRIPE_KEY]`). |
| **Block Task** | Instantly aborts the agent loop, flags status as `blocked`, and logs a security violation. |
| **Warn & Audit** | Allows the prompt to pass but logs an alert on the task scorecard. |

### Step 5: Test & Verify
1. Submit a test payload through the GuardLoop SDK or MCP Server containing sample sensitive data.
2. Observe the sanitized prompt in **Live Monitor** (`http://localhost:33000/monitor`).
3. Verify that the score engine logs the redaction event on the task's scorecard details.

---

## 📋 Default Pre-Packaged Detection Rules

GuardLoop comes out of the box with default patterns enabled:

| Rule Category | Pattern / Entity | Default Mask |
| :--- | :--- | :--- |
| **AWS Access Key** | `AKIA[0-9A-Z]{16}` | `[REDACTED_AWS_KEY]` |
| **Stripe Secret Key** | `sk_live_[0-9a-zA-Z]{24,}` | `[REDACTED_STRIPE_KEY]` |
| **Generic Secret / JWT** | `eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*` | `[REDACTED_JWT]` |
| **Social Security Number** | `\b\d{3}-\d{2}-\d{4}\b` | `[REDACTED_SSN]` |
| **Credit Card Number** | Presidio `CREDIT_CARD` / Luhn Check | `[REDACTED_CREDIT_CARD]` |

---

## 💻 API Reference Example

### Create a Dynamic PII Rule via REST API

```bash
curl -X POST http://localhost:38000/api/v1/pii-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gl_live_secret_key" \
  -d '{
    "name": "Custom Corporate Token",
    "category": "secret",
    "pattern_type": "regex",
    "pattern": "CORP-TOK-[A-Z0-9]{16}",
    "replacement_mask": "[REDACTED_CORP_TOKEN]",
    "action": "redact",
    "is_active": true
  }'
```
