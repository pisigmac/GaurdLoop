"""
TaskGraph Engine: Dependency-aware DAG scheduling with critical path analysis.
"""
from typing import List, Dict, Set, Optional
from collections import defaultdict, deque
import asyncio

class TaskGraphEngine:
    def __init__(self):
        self._tasks: Dict[str, dict] = {}
        self._edges: Dict[str, Set[str]] = defaultdict(set)  # task -> dependents
        self._reverse_edges: Dict[str, Set[str]] = defaultdict(set)  # task -> dependencies

    def add_task(self, task_id: str, duration_estimate: int = 60, priority: int = 5, status: str = "pending", name: str = ""):
        if task_id in self._tasks:
            self._tasks[task_id]["duration_estimate"] = duration_estimate
            self._tasks[task_id]["priority"] = priority
            if status != "pending":
                self._tasks[task_id]["status"] = status
            if name:
                self._tasks[task_id]["name"] = name
            return
        self._tasks[task_id] = {
            "id": task_id,
            "name": name,
            "duration_estimate": duration_estimate,
            "priority": priority,
            "status": status,
            "earliest_start": 0,
            "latest_start": float('inf'),
            "slack": 0,
        }

    def add_dependency(self, task_id: str, depends_on: str):
        """Task 'task_id' cannot start until 'depends_on' completes."""
        if task_id not in self._tasks:
            self.add_task(task_id)
        if depends_on not in self._tasks:
            self.add_task(depends_on)
        self._edges[depends_on].add(task_id)
        self._reverse_edges[task_id].add(depends_on)

    def get_ready_tasks(self) -> List[str]:
        """Tasks with no unmet dependencies."""
        ready = []
        for task_id, task in self._tasks.items():
            if task["status"] != "pending":
                continue
            deps = self._reverse_edges.get(task_id, set())
            if all(self._tasks.get(d, {}).get("status") == "completed" for d in deps):
                ready.append(task_id)
        # Sort by priority (lower number = higher priority)
        ready.sort(key=lambda t: self._tasks[t]["priority"])
        return ready

    def can_start(self, task_id: str) -> bool:
        deps = self._reverse_edges.get(task_id, set())
        return all(self._tasks.get(d, {}).get("status") == "completed" for d in deps)

    def mark_status(self, task_id: str, status: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = status

    def compute_critical_path(self) -> List[str]:
        """Forward pass to compute earliest start, backward pass for latest start."""
        if not self._tasks:
            return []

        # Topological sort
        in_degree = {tid: len(self._reverse_edges.get(tid, set())) for tid in self._tasks}
        queue = deque([t for t, d in in_degree.items() if d == 0])
        topo_order = []

        while queue:
            node = queue.popleft()
            topo_order.append(node)
            for neighbor in self._edges.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Forward pass
        earliest = {tid: 0 for tid in self._tasks}
        for tid in topo_order:
            finish = earliest[tid] + self._tasks[tid]["duration_estimate"]
            for neighbor in self._edges.get(tid, set()):
                earliest[neighbor] = max(earliest[neighbor], finish)

        project_duration = max(
            earliest[tid] + self._tasks[tid]["duration_estimate"]
            for tid in self._tasks
        ) if self._tasks else 0

        # Backward pass
        latest = {tid: project_duration for tid in self._tasks}
        for tid in reversed(topo_order):
            for neighbor in self._edges.get(tid, set()):
                latest[tid] = min(latest[tid], latest[neighbor] - self._tasks[tid]["duration_estimate"])

        # Slack and critical path
        critical = []
        for tid in self._tasks:
            slack = latest[tid] - earliest[tid]
            self._tasks[tid]["earliest_start"] = earliest[tid]
            self._tasks[tid]["latest_start"] = latest[tid]
            self._tasks[tid]["slack"] = slack
            if slack == 0:
                critical.append(tid)

        return critical

    def get_dependency_chain(self, task_id: str) -> List[str]:
        """All tasks that must complete before this task."""
        visited = set()
        chain = []

        def dfs(tid):
            if tid in visited:
                return
            visited.add(tid)
            for dep in self._reverse_edges.get(tid, set()):
                dfs(dep)
            chain.append(tid)

        dfs(task_id)
        return chain[:-1]  # Exclude self

    def to_dict(self) -> dict:
        return {
            "nodes": list(self._tasks.values()),
            "edges": [
                {"from": src, "to": dst}
                for src, dsts in self._edges.items()
                for dst in dsts
            ],
            "critical_path": self.compute_critical_path(),
            "ready_tasks": self.get_ready_tasks(),
        }
