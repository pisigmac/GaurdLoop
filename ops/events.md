# Events Catalog

## Webhook Sources

### Cursor
- `pr_opened` — New pull request created
- `pr_merged` — Pull request merged
- `issue_created` — Issue filed
- `automation_triggered` — Cursor Automation fired
- `code_change` — File modified by agent

### GitHub
- `pull_request.opened`
- `pull_request.synchronize`
- `issues.opened`
- `push` — Code pushed to branch

### Slack
- `message` — Channel message (filtered by keyword)

### Linear
- `Issue.created`
- `Issue.updated`

### PagerDuty
- `incident.triggered`
- `incident.resolved`

## Internal Events

- `task.created`
- `task.started`
- `task.completed`
- `task.failed`
- `task.blocked`
- `score.calculated`
- `score.overridden`
- `pii.blocked`
- `browser.verify_queued`
- `browser.verify_completed`
- `agent.connected`
- `agent.disconnected`
