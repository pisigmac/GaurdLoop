# Analytics & Events

## Tracked Events

| Event | Properties | Purpose |
|---|---|---|
| `task.created` | task_id, agent_type, priority | Funnel analysis |
| `task.started` | task_id, dependency_count | Queue performance |
| `task.completed` | task_id, duration_ms | Throughput |
| `task.blocked` | task_id, reason, score | Quality metrics |
| `score.calculated` | task_id, overall, decision | Score distribution |
| `score.overridden` | score_id, old_decision, new_decision | Override rate |
| `pii.blocked` | task_id, entity_types, secrets_count | Security posture |
| `browser.verify_passed` | task_id, url, a11y_count | UI quality |
| `webhook.received` | source, event_type, latency_ms | Integration health |
| `agent.connected` | agent_type, org_id | Adoption |

## Metrics

- **Task throughput**: tasks/hour
- **Average score**: rolling 7-day
- **Block rate**: % of tasks blocked
- **Override rate**: % of scores manually overridden
- **PII detection rate**: scans with findings / total scans
- **Browser pass rate**: % of verifications passing
- **Loop halt rate**: % of tasks stopped by LoopMonitor

## Dashboards

- Grafana: Backend metrics (Prometheus)
- Sentry: Error tracking
- PostHog: Product analytics (optional)
