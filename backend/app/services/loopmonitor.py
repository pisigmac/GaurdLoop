"""
LoopMonitor: Detects infinite loops, context bloat, and agent drift in real-time.
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class LoopState:
    iteration: int = 0
    context_size_tokens: int = 0
    last_action_hash: str = ""
    action_history: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    last_iteration_time: float = field(default_factory=time.time)
    warnings: List[str] = field(default_factory=list)
    should_halt: bool = False

class LoopMonitor:
    def __init__(
        self,
        max_iterations: int = 50,
        context_bloat_threshold: int = 8000,
        drift_similarity_threshold: float = 0.85,
        iteration_timeout_seconds: int = 300,
        on_halt: Optional[Callable] = None,
    ):
        self.max_iterations = max_iterations
        self.context_bloat_threshold = context_bloat_threshold
        self.drift_similarity_threshold = drift_similarity_threshold
        self.iteration_timeout_seconds = iteration_timeout_seconds
        self.on_halt = on_halt
        self._states: Dict[str, LoopState] = {}

    def start(self, task_id: str):
        self._states[task_id] = LoopState()

    def check(self, task_id: str, context_text: str, action_summary: str) -> LoopState:
        if task_id not in self._states:
            self.start(task_id)

        state = self._states[task_id]
        state.iteration += 1
        now = time.time()

        # 1. Infinite loop detection
        if state.iteration > self.max_iterations:
            state.warnings.append(f"Exceeded max iterations ({self.max_iterations})")
            state.should_halt = True

        # 2. Stuck detection (same action repeated)
        action_hash = hashlib.md5(action_summary.encode()).hexdigest()
        state.action_history.append(action_hash)

        if len(state.action_history) >= 3:
            last_three = state.action_history[-3:]
            if len(set(last_three)) == 1:
                state.warnings.append("Agent appears stuck: same action repeated 3 times")
                state.should_halt = True

        # 3. Context bloat
        # Approximate tokens: ~4 chars per token
        state.context_size_tokens = len(context_text) // 4
        if state.context_size_tokens > self.context_bloat_threshold:
            state.warnings.append(
                f"Context bloat detected: {state.context_size_tokens} tokens "
                f"(threshold: {self.context_bloat_threshold})"
            )

        # 4. Iteration timeout
        if now - state.last_iteration_time > self.iteration_timeout_seconds:
            state.warnings.append(
                f"Iteration timeout: {now - state.last_iteration_time:.0f}s "
                f"since last action"
            )
            state.should_halt = True

        # 5. Drift detection (simplified: check if recent actions are too similar)
        if len(state.action_history) >= 5:
            recent = state.action_history[-5:]
            unique = len(set(recent))
            if unique == 1:
                state.warnings.append("Severe drift: identical actions for 5 iterations")
                state.should_halt = True
            elif unique <= 2:
                state.warnings.append("Moderate drift: only 2 unique actions in last 5 iterations")

        # 6. Total task timeout (30 min default)
        if now - state.start_time > 1800:
            state.warnings.append("Total task timeout: 30 minutes exceeded")
            state.should_halt = True

        state.last_iteration_time = now
        state.last_action_hash = action_hash

        if state.should_halt and self.on_halt:
            self.on_halt(task_id, state)

        return state

    def get_state(self, task_id: str) -> Optional[LoopState]:
        return self._states.get(task_id)

    def reset(self, task_id: str):
        if task_id in self._states:
            del self._states[task_id]

    def summary(self, task_id: str) -> Dict:
        state = self._states.get(task_id)
        if not state:
            return {"error": "Task not found"}

        elapsed = time.time() - state.start_time
        avg_iteration_time = elapsed / max(state.iteration, 1)

        return {
            "task_id": task_id,
            "iterations": state.iteration,
            "elapsed_seconds": round(elapsed, 2),
            "avg_iteration_time": round(avg_iteration_time, 2),
            "context_size_tokens": state.context_size_tokens,
            "warnings": state.warnings,
            "should_halt": state.should_halt,
            "status": "halted" if state.should_halt else "healthy",
        }
