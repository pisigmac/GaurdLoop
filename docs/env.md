# Environment Variables

## Required

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | `postgresql+asyncpg://user:pass@host/db` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `SECRET_KEY` | App secret for JWT signing | `change-me-in-production` |
| `ENV` | Environment name | `development` / `production` |

## Auth

| Variable | Description |
|---|---|
| `CLERK_JWKS_URL` | Clerk JWKS endpoint for token verification |

## Webhooks

| Variable | Description |
|---|---|
| `WEBHOOK_SECRET` | HMAC secret for webhook signature verification |

## Payments

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe API key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook endpoint secret |

## Monitoring

| Variable | Description |
|---|---|
| `SENTRY_DSN` | Sentry error tracking DSN |

## Scoring (Optional — defaults in config)

| Variable | Default | Description |
|---|---|---|
| `AUTO_APPROVE_THRESHOLD` | 90 | Score to auto-approve |
| `HUMAN_REVIEW_THRESHOLD` | 70 | Score to flag for review |
| `BLOCK_THRESHOLD` | 50 | Score to block |
| `TEST_WEIGHT` | 0.40 | Test score weight |
| `COVERAGE_WEIGHT` | 0.25 | Coverage score weight |
| `SECURITY_WEIGHT` | 0.20 | Security score weight |
| `BEHAVIORAL_WEIGHT` | 0.15 | Behavioral score weight |
