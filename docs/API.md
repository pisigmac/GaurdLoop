# API Reference

## Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks (filter by status, agent_id) |
| GET | `/tasks/{id}` | Get task |
| PATCH | `/tasks/{id}` | Update task |
| POST | `/tasks/{id}/start` | Start task (checks deps) |
| POST | `/tasks/{id}/loop-check` | Submit loop state for monitoring |
| POST | `/tasks/{id}/score` | Calculate confidence score |
| GET | `/tasks/{id}/dependency-graph` | Get DAG visualization data |
| GET | `/tasks/{id}/stream` | SSE stream for live updates |

## Agents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/agents` | Register agent |
| GET | `/agents` | List agents |
| GET | `/agents/{id}` | Get agent |
| PATCH | `/agents/{id}` | Update agent config |
| DELETE | `/agents/{id}` | Remove agent |

## Scores

| Method | Endpoint | Description |
|---|---|---|
| GET | `/scores` | List scores |
| GET | `/scores/{id}` | Get score |
| POST | `/scores/{id}/override` | Override decision |

## PII

| Method | Endpoint | Description |
|---|---|---|
| POST | `/pii/scrub` | Scrub context for PII/secrets |
| GET | `/pii/scans/{task_id}` | Get scan history |

## Browser

| Method | Endpoint | Description |
|---|---|---|
| POST | `/browser/verify` | Queue browser verification |
| GET | `/browser/verifications/{task_id}` | Get results |

## Webhooks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/webhooks/ingest/{source}` | Ingest webhook |
| GET | `/webhooks` | List events |
| POST | `/webhooks/{id}/retry` | Retry failed event |

## SSE

| Method | Endpoint | Description |
|---|---|---|
| GET | `/sse/org/{org_id}` | Org-scoped event stream |
| GET | `/sse/global` | Global event stream |
