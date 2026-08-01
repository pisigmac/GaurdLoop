# Error Reference

## HTTP Status Codes

| Code | Meaning | When |
|---|---|---|
| 200 | OK | Standard success |
| 201 | Created | Resource created |
| 202 | Accepted | Async job queued |
| 400 | Bad Request | Invalid payload |
| 401 | Unauthorized | Missing/invalid JWT |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Dependency not met, duplicate |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Unexpected server error |

## Error Codes

| Code | Message | Resolution |
|---|---|---|
| `TASK_DEP_NOT_MET` | Dependencies not completed | Wait for parent tasks |
| `TASK_MAX_LOOPS` | Exceeded max iterations | Increase limit or fix agent |
| `AGENT_STUCK` | Agent repeating same action | Cancel and retry |
| `CONTEXT_BLOAT` | Context window too large | Trim history or split task |
| `PII_BLOCKED` | PII/secrets detected | Review and scrub context |
| `BROWSER_FAIL` | Browser verification failed | Fix UI issues |
| `SCORE_TOO_LOW` | Score below threshold | Fix tests/coverage/security |
| `WEBHOOK_INVALID_SIG` | Invalid webhook signature | Check secret configuration |
| `ADAPTER_NOT_FOUND` | Unknown agent type | Register adapter first |
| `RATE_LIMITED` | Too many requests | Wait or upgrade plan |
