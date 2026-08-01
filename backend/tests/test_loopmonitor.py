import pytest
from app.services.loopmonitor import LoopMonitor

class TestLoopMonitor:
    def test_max_iterations_halt(self):
        monitor = LoopMonitor(max_iterations=3)
        monitor.start("task-1")

        for i in range(3):
            state = monitor.check("task-1", f"context {i}", f"action {i}")

        assert state.should_halt
        assert any("Exceeded max iterations" in w for w in state.warnings)

    def test_stuck_detection(self):
        monitor = LoopMonitor()
        monitor.start("task-2")

        for _ in range(3):
            state = monitor.check("task-2", "same context", "same action")

        assert state.should_halt
        assert any("stuck" in w.lower() for w in state.warnings)

    def test_context_bloat_warning(self):
        monitor = LoopMonitor(context_bloat_threshold=10)
        monitor.start("task-3")

        big_context = "x" * 100  # ~25 tokens
        state = monitor.check("task-3", big_context, "action")

        assert not state.should_halt
        assert any("bloat" in w.lower() for w in state.warnings)
