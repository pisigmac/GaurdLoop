# Monitoring

## Sentry

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

## Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

http_requests_total = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
tasks_active = Gauge('guardloop_tasks_active', 'Active tasks', ['status'])
scores_calculated = Counter('guardloop_scores_calculated_total', 'Scores calculated', ['decision'])
pii_blocked = Counter('guardloop_pii_blocked_total', 'PII blocks')
```

## Alerts

| Alert | Condition | Severity |
|---|---|---|
| High error rate | > 1% 5xx in 5min | P1 |
| DB connection pool exhausted | > 90% used | P1 |
| Redis down | No ping response | P1 |
| High latency | p99 > 1s for 10min | P2 |
| Task queue backlog | > 100 pending | P2 |
| Browser verify failures | > 20% fail rate | P3 |
