# Testing Strategy

## Backend

### Unit Tests

| Module | Coverage Target | Status |
|---|---|---|
| TaskGraph Engine | 95% | Shipped |
| ScoreEngine | 95% | Shipped |
| ContextScrub | 90% | Shipped |
| LoopMonitor | 90% | Shipped |
| BrowserVerify | 80% | Shipped |

### Integration Tests

- Full task lifecycle: create -> start -> score -> complete
- Webhook ingestion -> task creation -> scoring pipeline
- SSE event streaming end-to-end
- PII blocking with real Presidio engine

### E2E Tests

- Docker Compose full stack spin-up
- Frontend -> Backend -> Database round-trip
- BrowserVerify with real Playwright container

## Frontend

- Vitest for component testing
- Playwright for E2E (separate from backend BrowserVerify)

## CI/CD

```yaml
# .github/workflows/ci.yml
- Run backend tests (pytest)
- Run frontend tests (vitest)
- Build Docker images
- Deploy to staging
- Run smoke tests
- Deploy to production
```
