# Data Retention

## GDPR / Privacy Compliance

| Data Type | Retention | Action After |
|---|---|---|
| Task output | 90 days | Anonymize, keep metadata |
| PII scan findings | 30 days | Delete raw findings, keep count |
| Browser screenshots | 14 days | Delete files, keep pass/fail |
| Webhook payloads | 30 days | Delete, keep event log |
| Audit logs | 7 years | Archive to cold storage |
| Score records | 2 years | Aggregate, delete details |
| User accounts | Until deletion | Soft delete, 30-day grace |

## Deletion API

```
DELETE /orgs/{id}/data-retention
Body: { "retention_days": 30, "data_types": ["tasks", "screenshots"] }
```

## Right to Erasure

User requests deletion -> Soft delete account -> 30-day grace -> Hard delete all personal data -> Keep anonymized aggregate metrics.
