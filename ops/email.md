# Email

## Provider
Postmark or Resend (transactional)

## Templates

### Welcome
Subject: "Your GuardLoop organization is ready"

### Score Alert
Subject: "Task blocked — score 45 (security issues found)"

### Weekly Digest
Subject: "Your GuardLoop weekly summary"
- Tasks completed
- Average score
- Blocked tasks
- PII scans run

### Billing
Subject: "Invoice from GuardLoop"

## Trigger Points
- Org creation -> Welcome
- Task blocked -> Score alert
- Score overridden -> Admin notification
- Weekly cron -> Digest
- Invoice paid/received -> Billing
