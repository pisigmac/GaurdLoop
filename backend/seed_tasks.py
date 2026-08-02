import httpx
import time

BASE_URL = "http://localhost:38000"

client = httpx.Client(timeout=30.0)

try:
    agents = client.get(f"{BASE_URL}/agents").json()
except Exception as e:
    agents = []

items = [
    {
        "name": "Refactor OAuth2 Refresh Token Rotation Protocol",
        "priority": 9,
        "output": {"tests_passed": 48, "tests_failed": 0, "line_coverage": 0.97, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Optimize PostgreSQL Composite Index for Task Search",
        "priority": 8,
        "output": {"tests_passed": 32, "tests_failed": 0, "line_coverage": 0.94, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Implement Redis PubSub Backpressure Buffer",
        "priority": 10,
        "output": {"tests_passed": 60, "tests_failed": 0, "line_coverage": 0.98, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Audit ContextScrub Presidio Engine Memory Usage",
        "priority": 7,
        "output": {"tests_passed": 25, "tests_failed": 0, "line_coverage": 0.91, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Add Dynamic Dark Mode Glassmorphism Theme to Dashboard",
        "priority": 5,
        "output": {"tests_passed": 18, "tests_failed": 0, "line_coverage": 0.89, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Implement Real-Time Webhook Rate Limiter with Leaky Bucket",
        "priority": 9,
        "output": {"tests_passed": 42, "tests_failed": 0, "line_coverage": 0.95, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Migrate Frontend State to Synchronous SessionStorage Hydration",
        "priority": 8,
        "output": {"tests_passed": 35, "tests_failed": 0, "line_coverage": 0.96, "sec_critical": 0, "sec_high": 0}
    },
    {
        "name": "Run Playwright Visual Regression Audit on Settings Page",
        "priority": 6,
        "output": {"tests_passed": 28, "tests_failed": 0, "line_coverage": 0.92, "sec_critical": 0, "sec_high": 0}
    }
]

print(f"Starting seeding of {len(items)} agent tasks...")

for i, item in enumerate(items):
    agent = agents[i % len(agents)] if agents else None
    agent_id = agent["id"] if agent else None
    agent_name = agent["name"] if agent else "Claude Code Assistant"

    # 1. Create Task
    task = client.post(f"{BASE_URL}/tasks", json={
        "name": item["name"],
        "agent_id": agent_id,
        "priority": item["priority"],
        "output": item["output"]
    }).json()
    task_id = task["id"]
    print(f"[{i+1}/{len(items)}] Created: '{item['name']}' → Assigned to {agent_name}")

    # 2. Start Task
    client.post(f"{BASE_URL}/tasks/{task_id}/start")
    
    # 3. Perform Loop Check
    client.post(f"{BASE_URL}/tasks/{task_id}/loop-check", params={
        "context_text": f"Executing step {i+1} for {item['name']}",
        "action_summary": f"Iteration {i+1} verified"
    })

    # 4. Scrub Context for PII
    client.post(f"{BASE_URL}/pii/scrub", json={
        "task_id": task_id,
        "context_text": f"Internal audit log for {item['name']} token=sk_live_demo1234567890",
        "strict_mode": False
    })

    # 5. Calculate Score
    score = client.post(f"{BASE_URL}/tasks/{task_id}/score").json()
    overall = score.get("overall", 0)
    decision = score.get("decision", "").upper()
    print(f"     ↳ Overall Score: {overall} [{decision}]")

    time.sleep(0.3)

print("\nSuccessfully pushed all agent tasks!")
