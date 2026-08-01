# GuardLoop Python SDK

Programmatic access to the GuardLoop Agent Trust Layer.

## Install

```bash
pip install guardloop-sdk
```

## Quick Start

```python
from guardloop_sdk import GuardLoopClient

client = GuardLoopClient(api_key="gl_...", base_url="https://api.guardloop.dev")

# Create a task
task = client.tasks.create(
    name="Refactor auth middleware",
    agent_id="cursor-agent-123",
    priority=5,
    max_loops=50,
)

# Start it
client.tasks.start(task.id)

# Score it
score = client.tasks.score(task.id)
print(f"Score: {score.overall} — Decision: {score.decision}")

if score.blocked:
    print("Do not merge. Fix issues first.")
elif score.needs_review:
    print("Needs human review before merging.")
elif score.passed:
    print("Auto-approved. Safe to merge.")

# Stream real-time events
for event in client.tasks.stream(task.id):
    print(event)

# Scrub context for PII before sending to LLM
result = client.pii.scrub(
    task_id=task.id,
    context_text="Contact john@example.com for details. AWS key: AKIA...",
    strict_mode=True,
)
if result["blocked"]:
    print(f"Blocked: {result['block_reason']}")

# Verify browser output
client.browser.verify(
    task_id=task.id,
    url="http://localhost:3000",
    viewport_width=1280,
    viewport_height=720,
)
```

## Resources

- `client.tasks` — Task CRUD, start, score, dependency graph, stream
- `client.agents` — Agent registration, list, update, delete
- `client.scores` — Score listing, override decisions
- `client.pii` — Context scrubbing, scan history
- `client.browser` — Browser verification, results
