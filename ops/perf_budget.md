# Performance Budget

## Backend

| Metric | Target | Alert At |
|---|---|---|
| API p50 latency | < 50ms | 100ms |
| API p99 latency | < 500ms | 1000ms |
| DB query time | < 20ms | 50ms |
| Redis op time | < 5ms | 10ms |
| Score calculation | < 200ms | 500ms |
| Browser verify | < 30s | 60s |

## Frontend

| Metric | Target | Alert At |
|---|---|---|
| First Contentful Paint | < 1.0s | 1.5s |
| Largest Contentful Paint | < 2.5s | 3.5s |
| Time to Interactive | < 3.0s | 4.0s |
| Bundle size (initial) | < 200KB | 300KB |

## Monitoring

- Prometheus: `http_request_duration_seconds`, `db_query_duration_seconds`
- Sentry: Performance monitoring
- Lighthouse CI: PR-level budget enforcement
