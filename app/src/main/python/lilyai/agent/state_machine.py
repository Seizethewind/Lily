"""Task lifecycle state machine (notes section 11)."""
import threading
from enum import Enum


class TaskState(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    NEEDS_USER_INPUT = "NEEDS_USER_INPUT"


S = TaskState
# The notes list all of these as terminal. Resuming means creating a new task
# (this also prevents accidental duplicate execution of the old one).
FINAL_STATES = frozenset({S.COMPLETED, S.FAILED, S.CANCELLED, S.BLOCKED, S.NEEDS_USER_INPUT})
_STOPS = {S.FAILED, S.CANCELLED, S.BLOCKED, S.NEEDS_USER_INPUT}
_ALLOWED = {
    S.CREATED: {S.PLANNING, S.CANCELLED, S.FAILED},
    S.PLANNING: {S.AWAITING_APPROVAL, S.RUNNING} | _STOPS,
    S.AWAITING_APPROVAL: {S.RUNNING} | _STOPS,
    S.RUNNING: {S.AWAITING_APPROVAL, S.VERIFYING, S.COMPLETED} | _STOPS,
    S.VERIFYING: {S.AWAITING_APPROVAL, S.RUNNING, S.COMPLETED} | _STOPS,
}


class IllegalTransition(Exception):
    pass


class StateMachine:
    """One authoritative, thread-safe state per task."""

    def __init__(self, initial=TaskState.CREATED):
        self._state = initial
        self._lock = threading.Lock()

    @property
    def state(self):
        return self._state

    @property
    def is_final(self):
        return self._state in FINAL_STATES

    def can_transition(self, new):
        return new in _ALLOWED.get(self._state, ())

    def transition(self, new):
        with self._lock:
            if new not in _ALLOWED.get(self._state, ()):
                raise IllegalTransition(f"{self._state.value} -> {new.value} is not allowed")
            self._state = new
            return new
