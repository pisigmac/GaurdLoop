import pytest
from app.services.taskgraph import TaskGraphEngine

class TestTaskGraphEngine:
    def test_add_task_and_dependency(self):
        engine = TaskGraphEngine()
        engine.add_task("A", duration_estimate=60)
        engine.add_task("B", duration_estimate=30)
        engine.add_dependency("B", "A")

        assert not engine.can_start("B")
        engine.mark_status("A", "completed")
        assert engine.can_start("B")

    def test_critical_path(self):
        engine = TaskGraphEngine()
        for tid, dur in [("A", 10), ("B", 20), ("C", 15), ("D", 5)]:
            engine.add_task(tid, duration_estimate=dur)
        engine.add_dependency("B", "A")
        engine.add_dependency("C", "A")
        engine.add_dependency("D", "B")
        engine.add_dependency("D", "C")

        critical = engine.compute_critical_path()
        assert "A" in critical
        assert "D" in critical

    def test_ready_tasks_priority(self):
        engine = TaskGraphEngine()
        engine.add_task("A", priority=3)
        engine.add_task("B", priority=1)
        engine.add_task("C", priority=5)

        ready = engine.get_ready_tasks()
        assert ready == ["B", "A", "C"]  # Sorted by priority
