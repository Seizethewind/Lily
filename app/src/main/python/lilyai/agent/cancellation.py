"""Cooperative cancellation shared by every executing component (notes section 6)."""
import logging
import threading
from enum import Enum

log = logging.getLogger(__name__)


class CancellationState(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    REQUESTED = "REQUESTED"
    IN_PROGRESS = "IN_PROGRESS"
    STOPPED = "STOPPED"
    UNRESPONSIVE = "UNRESPONSIVE"      # a component did not respond to cancellation


class CancelledError(Exception):
    pass


_OPEN = (CancellationState.REQUESTED, CancellationState.IN_PROGRESS)


class CancellationToken:
    def __init__(self):
        self._lock = threading.Lock()
        self._state = CancellationState.NOT_REQUESTED
        self._callbacks = []
        self._event = threading.Event()
        self.reason = ""

    @property
    def state(self):
        return self._state

    @property
    def is_cancelled(self):
        return self._state is not CancellationState.NOT_REQUESTED

    def request(self, reason=""):
        """Register a stop request. Returns False if one was already registered."""
        with self._lock:
            if self.is_cancelled:
                return False
            self._state = CancellationState.REQUESTED
            self.reason = reason
            callbacks, self._callbacks = self._callbacks, []
            self._event.set()
        for cb in callbacks:
            self._run(cb)
        return True

    def add_callback(self, callback):
        """Run callback on cancellation (immediately if already cancelled)."""
        with self._lock:
            if not self.is_cancelled:
                self._callbacks.append(callback)
                return
        self._run(callback)

    @staticmethod
    def _run(callback):
        try:
            callback()
        except Exception:  # a failing callback must not block other cleanup
            log.exception("cancellation callback failed")

    def raise_if_cancelled(self):
        if self.is_cancelled:
            raise CancelledError(self.reason or "cancelled")

    def wait(self, timeout=None):
        return self._event.wait(timeout)

    def _move(self, new):
        with self._lock:
            if self._state in _OPEN:
                self._state = new

    def mark_in_progress(self):
        with self._lock:
            if self._state is CancellationState.REQUESTED:
                self._state = CancellationState.IN_PROGRESS

    def mark_stopped(self):
        self._move(CancellationState.STOPPED)

    def mark_unresponsive(self):
        self._move(CancellationState.UNRESPONSIVE)
