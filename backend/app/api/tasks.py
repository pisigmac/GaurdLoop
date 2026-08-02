from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from typing import List
from app.core.database import get_db
from app.core.redis import get_redis, broadcast_event
from app.models.task import Task
from app.models.agent import Agent
from app.models.score import Score
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskDependencyGraph
from app.services.taskgraph import TaskGraphEngine
from app.services.scoreengine import ScoreEngine, TestResults, CoverageReport, SecurityScan, BehavioralCheck
from app.services.loopmonitor import LoopMonitor

router = APIRouter(prefix="/tasks", tags=["tasks"])

loop_monitor = LoopMonitor(max_iterations=50)

async def _get_agent_name(db: AsyncSession, agent_id: str | None) -> str:
    if not agent_id:
        return "System Agent"
    res = await db.execute(select(Agent.name).where(Agent.id == agent_id))
    name = res.scalar_one_or_none()
    return name or "Agent"

@router.post("", response_model=TaskOut)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        name=data.name,
        description=data.description,
        agent_id=data.agent_id,
        parent_ids=data.parent_ids,
        priority=data.priority,
        max_loops=data.max_loops,
        current_loop=data.current_loop or 0,
        context_size_tokens=data.context_size_tokens or 0,
        context_window=data.context_window,
        output=data.output or {},
        scheduled_at=data.scheduled_at,
        org_id="default-org",  # TODO: from auth
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    agent_name = await _get_agent_name(db, task.agent_id)

    # Publish to Redis for task queue & live monitor SSE
    redis = await get_redis()
    await redis.publish("guardloop:tasks:new", str(task.id))
    await broadcast_event("default-org", "task_created", {
        "task_id": str(task.id),
        "name": task.name,
        "agent_id": task.agent_id,
        "agent_name": agent_name,
        "status": task.status
    })

    return task

@router.get("", response_model=List[TaskOut])
async def list_tasks(
    status: str = None,
    agent_id: str = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.org_id == "default-org")
    if status:
        query = query.where(Task.status == status)
    if agent_id:
        query = query.where(Task.agent_id == agent_id)
    query = query.order_by(Task.priority, Task.created_at)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    agent_name = await _get_agent_name(db, task.agent_id)
    await broadcast_event("default-org", "task_updated", {
        "task_id": str(task.id),
        "name": task.name,
        "agent_id": task.agent_id,
        "agent_name": agent_name,
        "status": task.status
    })
    return task

@router.post("/{task_id}/start")
async def start_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check dependencies
    engine = TaskGraphEngine()
    for dep_id in task.parent_ids or []:
        dep_result = await db.execute(select(Task).where(Task.id == dep_id))
        dep = dep_result.scalar_one_or_none()
        if dep and dep.status != "completed":
            raise HTTPException(
                status_code=409,
                detail=f"Dependency {dep_id} not completed (status: {dep.status})"
            )
        engine.add_dependency(task_id, dep_id)

    if not engine.can_start(task_id):
        raise HTTPException(status_code=409, detail="Dependencies not met")

    task.status = "running"
    task.started_at = func.now()
    if task.current_loop == 0:
        task.current_loop = 1
    await db.commit()

    agent_name = await _get_agent_name(db, task.agent_id)

    # Start loop monitoring
    loop_monitor.start(task_id)
    await broadcast_event("default-org", "task_started", {
        "task_id": str(task_id),
        "name": task.name,
        "agent_id": task.agent_id,
        "agent_name": agent_name,
        "status": "running"
    })

    return {"status": "started", "task_id": task_id}

@router.post("/{task_id}/loop-check")
async def check_loop(
    task_id: str,
    context_text: str,
    action_summary: str,
    db: AsyncSession = Depends(get_db),
):
    state = loop_monitor.check(task_id, context_text, action_summary)

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    agent_name = "Agent"
    if task:
        task.current_loop = state.iteration
        task.context_size_tokens = state.context_size_tokens
        if state.should_halt:
            task.status = "blocked"
            task.error_log = "; ".join(state.warnings)
        await db.commit()
        agent_name = await _get_agent_name(db, task.agent_id)

    await broadcast_event("default-org", "loop_checked", {
        "task_id": str(task_id),
        "name": task.name if task else "Task",
        "agent_id": task.agent_id if task else None,
        "agent_name": agent_name,
        "iteration": state.iteration,
        "tokens": state.context_size_tokens,
        "should_halt": state.should_halt,
        "warnings": state.warnings
    })

    return loop_monitor.summary(task_id)

@router.post("/{task_id}/score")
async def calculate_score(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Build score from task output
    output = task.output or {}

    tests = TestResults(
        passed=output.get("tests_passed", 0),
        failed=output.get("tests_failed", 0),
        skipped=output.get("tests_skipped", 0),
        duration_ms=output.get("test_duration_ms", 0),
        flaky_detected=output.get("flaky_detected", False),
    )

    coverage = CoverageReport(
        line_coverage=output.get("line_coverage", 0.0),
        branch_coverage=output.get("branch_coverage", 0.0),
        function_coverage=output.get("function_coverage", 0.0),
    )

    security = SecurityScan(
        critical=output.get("sec_critical", 0),
        high=output.get("sec_high", 0),
        medium=output.get("sec_medium", 0),
        low=output.get("sec_low", 0),
        secrets_exposed=output.get("secrets_exposed", 0),
    )

    behavioral = BehavioralCheck(
        no_infinite_loops=not loop_monitor.get_state(task_id).should_halt if loop_monitor.get_state(task_id) else True,
        no_context_bloat=(task.context_size_tokens or 0) < 8000,
        no_agent_drift=True,
        browser_passed=output.get("browser_passed", True),
    )

    engine = ScoreEngine()
    res_score = engine.calculate(tests, coverage, security, behavioral)

    score = Score(
        task_id=task_id,
        org_id=task.org_id,
        overall=res_score["overall"],
        test_score=res_score["test_score"],
        coverage_score=res_score["coverage_score"],
        security_score=res_score["security_score"],
        behavioral_score=res_score["behavioral_score"],
        weights=res_score["weights"],
        test_details=res_score["details"]["tests"],
        security_details=res_score["details"]["security"],
        behavioral_details=res_score["details"]["behavioral"],
        decision=res_score["decision"],
    )
    db.add(score)
    await db.commit()

    # Update task status based on decision
    if res_score["decision"] == "block":
        task.status = "blocked"
    else:
        task.status = "completed"
    task.completed_at = func.now()

    await db.commit()

    agent_name = await _get_agent_name(db, task.agent_id)

    await broadcast_event("default-org", "score_calculated", {
        "task_id": str(task_id),
        "name": task.name,
        "agent_id": task.agent_id,
        "agent_name": agent_name,
        "overall": res_score["overall"],
        "decision": res_score["decision"]
    })

    return res_score

@router.get("/{task_id}/dependency-graph")
async def get_dependency_graph(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task).where(Task.org_id == "default-org")
    )
    tasks = result.scalars().all()

    # Find all tasks involved in dependencies
    connected_ids = set()
    for t in tasks:
        if t.parent_ids:
            connected_ids.add(t.id)
            for p in t.parent_ids:
                connected_ids.add(p)

    # Sort so connected tasks come first
    sorted_tasks = sorted(tasks, key=lambda x: (0 if x.id in connected_ids else 1, x.created_at))

    engine = TaskGraphEngine()
    for t in sorted_tasks:
        engine.add_task(t.id, duration_estimate=60, priority=t.priority, status=t.status, name=t.name)

    for t in sorted_tasks:
        for dep in (t.parent_ids or []):
            engine.add_dependency(t.id, dep)

    graph = engine.to_dict()
    critical = engine.compute_critical_path()

    return TaskDependencyGraph(
        nodes=graph["nodes"],
        edges=graph["edges"],
        critical_path=critical,
        estimated_duration_seconds=sum(
            engine._tasks.get(tid, {}).get("duration_estimate", 60) for tid in critical
        ) if critical else 0,
    )

@router.get("/{task_id}/stream")
async def stream_task(task_id: str):
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        redis = await get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"guardloop:task:{task_id}")

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = json.dumps({
                        "type": "task_update",
                        "task_id": task_id,
                        "data": message.get("data", {}),
                        "timestamp": asyncio.get_event_loop().time(),
                    })
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.5)
        finally:
            await pubsub.unsubscribe(f"guardloop:task:{task_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
