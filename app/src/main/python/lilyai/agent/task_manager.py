"""Supervised task runtime: policy checks, approval, cancellation and logging (notes sections 6, 11, 12).

The task runtime is separate from the language model: a model-generated plan is never executable
authority. Every step is validated, checked against the policy and (if required) approved immediately
before it runs, so a retry can never bypass an approval.
"""
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ..config import DEFAULT_CONFIG
from ..permissions.policy import Decision
from ..tools.registry import ToolError
from .cancellation import CancellationToken, CancelledError
from .state_machine import IllegalTransition, StateMachine, TaskState

# approver(task_id, tool_name, args, token) -> True to approve. Runs on the worker thread.
Approver = Callable[[str, str, Dict[str, Any], CancellationToken], bool]


class DuplicateTaskError(Exception):
    pass


class UnknownTaskError(KeyError):
    pass


class SessionError(Exception):
    pass


@dataclass
class StepResult:
    ok: bool
    output: Any = None
    error: Optional[str] = None
    state: Optional[TaskState] = None


class Task:
    def __init__(self, goal, dedupe_key=None):
        self.id = uuid.uuid4().hex
        self.goal = goal
        self.dedupe_key = dedupe_key
        self.token = CancellationToken()
        self.machine = StateMachine()
        self.step_lock = threading.Lock()      # one step at a time; Stop never needs this lock

    @property
    def state(self):
        return self.machine.state


class AutomationSession:
    """Repetitive automation: needs approval, has a hard run cap, stops on unexpected conditions."""

    def __init__(self, goal, max_runs=DEFAULT_CONFIG.max_runs_per_session):
        if not 1 <= max_runs <= DEFAULT_CONFIG.max_runs_per_session:
            raise ValueError(f"max_runs must be between 1 and {DEFAULT_CONFIG.max_runs_per_session}")
        self.goal = goal
        self.max_runs = max_runs
        self.token = CancellationToken()
        self._approved = False
        self._runs = 0
        self._lock = threading.Lock()

    @property
    def runs(self):
        return self._runs

    def approve(self):
        self._approved = True

    def stop(self, reason):
        self.token.request(reason)

    def start_run(self):
        with self._lock:
            if self.token.is_cancelled:
                raise SessionError(f"session stopped: {self.token.reason}")
            if not self._approved:
                raise SessionError("session has not been approved")
            if self._runs >= self.max_runs:
                raise SessionError("session run limit reached")
            self._runs += 1
            return self._runs


def _summarize(value, limit=200):
    text = f"{type(value).__name__}: {value!r}"
    return text if len(text) <= limit else text[:limit] + "..."


class TaskManager:
    def __init__(self, registry, policy, log=None, approver: Optional[Approver] = None):
        self._registry = registry
        self._policy = policy
        self._log = log
        self._approver = approver
        self._tasks = {}
        self._lock = threading.Lock()

    # -- task bookkeeping -------------------------------------------------
    def create_task(self, goal, dedupe_key=None):
        with self._lock:
            if dedupe_key is not None:
                for other in self._tasks.values():
                    if other.dedupe_key == dedupe_key and not other.machine.is_final:
                        raise DuplicateTaskError(f"an active task already exists for {dedupe_key!r}")
            task = Task(goal, dedupe_key)
            self._tasks[task.id] = task
        self._record(task, "task_created", summary=goal)
        return task

    def get(self, task_id):
        try:
            return self._tasks[task_id]
        except KeyError:
            raise UnknownTaskError(task_id) from None

    def _record(self, task, event_type, **fields):
        if self._log is not None:
            self._log.record(task.id, event_type, state=task.state.value,
                             cancellation_state=task.token.state.value, **fields)

    def _enter(self, task, new):
        if task.state is not new:
            task.machine.transition(new)

    def _end(self, task, new_state, event_type, **fields):
        try:
            if not task.machine.is_final:
                task.machine.transition(new_state)
        except IllegalTransition:
            pass
        self._record(task, event_type, **fields)

    def _finalize_cancelled(self, task, reason="cancelled"):
        if not task.machine.is_final:
            self._end(task, TaskState.CANCELLED, "task_stopped", summary=reason)
            task.token.mark_stopped()

    def _cancelled_result(self, task):
        self._finalize_cancelled(task, task.token.reason or "cancelled")
        return StepResult(False, error="cancelled", state=task.state)

    # -- execution ----------------------------------------------------------
    def run_step(self, task_id, tool_name, args):
        task = self.get(task_id)
        with task.step_lock:
            args = dict(args)
            if task.machine.is_final:
                return StepResult(False, error=f"task is {task.state.value}", state=task.state)
            if task.state is TaskState.CREATED:
                self._enter(task, TaskState.PLANNING)
            if task.token.is_cancelled:
                return self._cancelled_result(task)
            try:
                tool = self._registry.get(tool_name)
                self._registry.validate(tool_name, args)
            except ToolError as exc:
                self._record(task, "action_failed", tool=tool_name,
                             error_category="invalid_tool_call", error_message=str(exc))
                return StepResult(False, error=str(exc), state=task.state)

            verdict = self._policy.evaluate(tool_name, args)
            if verdict.decision is Decision.DENY:
                self._end(task, TaskState.BLOCKED, "action_blocked", tool=tool_name, summary=verdict.reason)
                return StepResult(False, error=verdict.reason, state=task.state)

            approval = "not_required"
            if verdict.decision is Decision.REQUIRE_APPROVAL:
                if self._approver is None:
                    reason = "approval is required but no approver is available"
                    self._end(task, TaskState.BLOCKED, "action_blocked", tool=tool_name, summary=reason)
                    return StepResult(False, error=reason, state=task.state)
                self._enter(task, TaskState.AWAITING_APPROVAL)
                self._record(task, "approval_requested", tool=tool_name, approval="requested", summary=verdict.reason)
                try:
                    granted = bool(self._approver(task.id, tool_name, dict(args), task.token))
                except Exception:
                    granted = False
                if task.token.is_cancelled:
                    return self._cancelled_result(task)
                if not granted:
                    task.token.request("approval rejected")
                    self._record(task, "approval_rejected", tool=tool_name, approval="rejected")
                    return self._cancelled_result(task)
                approval = "granted"
                self._record(task, "approval_granted", tool=tool_name, approval=approval)

            self._enter(task, TaskState.RUNNING)
            if task.token.is_cancelled:            # last check before anything touches the device
                return self._cancelled_result(task)
            self._record(task, "tool_started", tool=tool_name, approval=approval)
            try:
                output = tool.run(args, task.token)
            except CancelledError:
                return self._cancelled_result(task)
            except Exception as exc:
                self._end(task, TaskState.FAILED, "action_failed", tool=tool_name,
                          error_category=type(exc).__name__, error_message=str(exc))
                return StepResult(False, error=str(exc), state=task.state)
            if task.token.is_cancelled:
                return self._cancelled_result(task)
            self._record(task, "tool_completed", tool=tool_name, summary=_summarize(output))
            return StepResult(True, output=output, state=task.state)

    def verify(self, task_id):
        task = self.get(task_id)
        self._enter(task, TaskState.VERIFYING)
        self._record(task, "action_verification_started")

    def complete(self, task_id, summary=None):
        task = self.get(task_id)
        self._enter(task, TaskState.COMPLETED)
        self._record(task, "task_completed", summary=summary)

    def fail(self, task_id, reason):
        self._end(self.get(task_id), TaskState.FAILED, "task_failed", error_message=reason)

    def request_stop(self, task_id, reason="stop requested"):
        """Registers the stop immediately. If a step is running it finalizes the task when it unwinds;
        otherwise the task is cancelled right away. Returns the cancellation state so the UI can be truthful."""
        task = self.get(task_id)
        if task.token.request(reason):
            self._record(task, "cancellation_requested", summary=reason)
        if task.step_lock.acquire(blocking=False):
            try:
                self._finalize_cancelled(task, reason)
            finally:
                task.step_lock.release()
        return task.token.state
