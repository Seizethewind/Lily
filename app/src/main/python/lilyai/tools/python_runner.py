"""Bounded, cancellable execution of Python scripts and approved commands (notes section 10).

Subprocess behaviour inside the APK (sys.executable, process groups, threading) is PENDING TEST on the
OPPO A92 (Milestone 2/8). `executable` is injectable so the embedded-Python strategy can supply its own.
"""
import os
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

from ..agent.cancellation import CancellationToken
from ..config import DEFAULT_CONFIG
from .registry import Tool

_POLL = 0.1
_SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


@dataclass(frozen=True)
class RunResult:
    exit_code: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool
    cancelled: bool

    @property
    def ok(self):
        return self.exit_code == 0 and not self.timed_out and not self.cancelled


def _clean_env():
    """Child processes never inherit credentials such as the Tavily key."""
    return {k: v for k, v in os.environ.items() if not any(h in k.upper() for h in _SECRET_HINTS)}


def _signal(proc, sig):
    try:
        if os.name == "posix":
            os.killpg(proc.pid, sig)
        elif sig == signal.SIGTERM:
            proc.terminate()
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _terminate(proc, grace=2.0):
    """Returns True if the process is gone."""
    if proc.poll() is not None:
        return True
    _signal(proc, signal.SIGTERM)
    try:
        proc.wait(timeout=grace)
        return True
    except subprocess.TimeoutExpired:
        pass
    _signal(proc, getattr(signal, "SIGKILL", signal.SIGTERM))
    try:
        proc.wait(timeout=grace)
        return True
    except subprocess.TimeoutExpired:
        return False


def _trunc(text, limit):
    return text if len(text) <= limit else text[:limit] + "\n[output truncated]"


def _run_process(argv, *, timeout, token, output_limit):
    token = token or CancellationToken()
    if token.is_cancelled:
        return RunResult(None, "", "", False, True)
    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
            text=True, errors="replace", env=_clean_env(), start_new_session=(os.name == "posix"))
    except OSError as exc:
        return RunResult(None, "", f"could not start process: {exc}", False, False)
    deadline = time.monotonic() + timeout
    timed_out = cancelled = False
    while True:
        try:
            out, err = proc.communicate(timeout=_POLL)
            break
        except subprocess.TimeoutExpired:
            pass
        if token.is_cancelled:
            cancelled = True
            token.mark_in_progress()
        elif time.monotonic() >= deadline:
            timed_out = True
        else:
            continue
        stopped = _terminate(proc)
        if cancelled:
            token.mark_stopped() if stopped else token.mark_unresponsive()
        try:
            out, err = proc.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            out = err = ""
        break
    return RunResult(proc.returncode, _trunc(out, output_limit), _trunc(err, output_limit), timed_out, cancelled)


def run_script(code, *, timeout=DEFAULT_CONFIG.script_timeout_seconds, token=None, executable=None,
               output_limit=DEFAULT_CONFIG.output_limit_chars):
    return _run_process([executable or sys.executable, "-I", "-c", code],
                        timeout=timeout, token=token, output_limit=output_limit)


def run_command(command, *, timeout=DEFAULT_CONFIG.script_timeout_seconds, token=None,
                output_limit=DEFAULT_CONFIG.output_limit_chars):
    """Runs one command without a shell. Authorization is the PermissionPolicy's job, not this function's."""
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return RunResult(None, "", f"could not parse command: {exc}", False, False)
    if not argv:
        return RunResult(None, "", "empty command", False, False)
    return _run_process(argv, timeout=timeout, token=token, output_limit=output_limit)


def python_tool(*, timeout=DEFAULT_CONFIG.script_timeout_seconds, executable=None):
    return Tool("python.run", "Run a Python script in a separate process.", {"code": str},
                lambda args, token: run_script(args["code"], timeout=timeout, token=token, executable=executable),
                required=("code",))


def terminal_tool(*, timeout=DEFAULT_CONFIG.script_timeout_seconds):
    return Tool("terminal.command", "Run one terminal command (no shell).", {"command": str},
                lambda args, token: run_command(args["command"], timeout=timeout, token=token),
                required=("command",))
