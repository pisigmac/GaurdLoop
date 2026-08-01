# Staging Environment

## Parity Checklist

- [ ] Same K8s version as production
- [ ] Same Postgres version (15)
- [ ] Same Redis version (7)
- [ ] Same container images (different tag)
- [ ] Same resource limits (scaled down replicas)
- [ ] Same secrets structure (different values)
- [ ] Same ingress configuration (different domain)
- [ ] Same feature flags
- [ ] Same rate limits (higher for testing)
- [ ] Stripe test mode
- [ ] Clerk test instance
- [ ] Sentry staging project

## Domain
staging.guardloop.dev

## Data
- Reset before each deploy
- Seed with synthetic data
- No production PII

## CI/CD
```yaml
# .github/workflows/deploy-staging.yml
on:
  push:
    branches: [main]
jobs:
  deploy:
    steps:
      - build images
      - push to staging registry
      - kubectl apply -f infra/k8s/ -n guardloop-staging
      - run smoke tests
      - notify Slack
```
