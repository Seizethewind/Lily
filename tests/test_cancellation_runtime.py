"""Stop must be a real execution capability, not a decorative button."""
import threading
import time
import unittest

from lilyai.agent.cancellation import CancellationState as C, CancelledError
from lilyai.agent.state_machine import TaskState as S
from lilyai.agent.task_manager import AutomationSession, DuplicateTaskError, SessionError, TaskManager
from lilyai.history.task_log import TaskLog
from lilyai.permissions.policy import Decision as D, PermissionPolicy
from lilyai.tools.registry import Tool, ToolRegistry


class Harness:
    def __init__(self, decision=D.ALLOW, approver=None):
        self.ran = []
        self.started = threading.Event()
        reg = ToolRegistry()
        reg.register(Tool("act", "d", {"v": int}, lambda a, t: self.ran.append(a) or "done", required=("v",)))
        reg.register(Tool("slow", "d", {}, self._slow))
        self.log = TaskLog()
        self.tm = TaskManager(reg, PermissionPolicy({"act": decision, "slow": D.ALLOW}), self.log, approver)

    def _slow(self, args, token):
        self.started.set()
        while not token.is_cancelled:
            time.sleep(0.01)
        raise CancelledError()

    def events(self, task):
        return [e["event_type"] for e in self.log.events(task.id)]


class TaskRuntimeTests(unittest.TestCase):
    def test_allowed_step_runs_and_completes(self):
        h = Harness()
        t = h.tm.create_task("g")
        r = h.tm.run_step(t.id, "act", {"v": 1})
        self.assertTrue(r.ok)
        self.assertEqual((r.output, t.state), ("done", S.RUNNING))
        h.tm.verify(t.id)
        h.tm.complete(t.id)
        self.assertEqual(t.state, S.COMPLETED)
        self.assertIn("tool_completed", h.events(t))

    def test_deny_blocks_task_without_running(self):
        h = Harness(decision=D.DENY)
        t = h.tm.create_task("g")
        self.assertFalse(h.tm.run_step(t.id, "act", {"v": 1}).ok)
        self.assertEqual((t.state, h.ran), (S.BLOCKED, []))

    def test_approval_required_without_approver_blocks(self):
        h = Harness(decision=D.REQUIRE_APPROVAL)
        t = h.tm.create_task("g")
        h.tm.run_step(t.id, "act", {"v": 1})
        self.assertEqual((t.state, h.ran), (S.BLOCKED, []))

    def test_rejected_approval_cancels_without_running(self):
        h = Harness(decision=D.REQUIRE_APPROVAL, approver=lambda *a: False)
        t = h.tm.create_task("g")
        h.tm.run_step(t.id, "act", {"v": 1})
        self.assertEqual((t.state, h.ran), (S.CANCELLED, []))
        self.assertIn("approval_rejected", h.events(t))

    def test_every_step_asks_again_so_retries_cannot_bypass_approval(self):
        asked = []
        h = Harness(decision=D.REQUIRE_APPROVAL, approver=lambda *a: asked.append(1) or True)
        t = h.tm.create_task("g")
        h.tm.run_step(t.id, "act", {"v": 1})
        h.tm.run_step(t.id, "act", {"v": 1})
        self.assertEqual((len(asked), len(h.ran)), (2, 2))

    def test_invalid_call_is_reported_not_fatal(self):
        h = Harness()
        t = h.tm.create_task("g")
        self.assertFalse(h.tm.run_step(t.id, "act", {"v": "x"}).ok)
        self.assertFalse(h.tm.run_step(t.id, "nope", {}).ok)
        self.assertTrue(h.tm.run_step(t.id, "act", {"v": 1}).ok)

    def test_stop_before_step_prevents_execution(self):
        h = Harness()
        t = h.tm.create_task("g")
        self.assertEqual(h.tm.request_stop(t.id), C.STOPPED)
        self.assertEqual(t.state, S.CANCELLED)
        self.assertFalse(h.tm.run_step(t.id, "act", {"v": 1}).ok)
        self.assertEqual(h.ran, [])

    def test_stop_during_running_tool_cancels_and_reports(self):
        h = Harness()
        t = h.tm.create_task("g")
        out = []
        th = threading.Thread(target=lambda: out.append(h.tm.run_step(t.id, "slow", {})))
        th.start()
        self.assertTrue(h.started.wait(2))
        self.assertEqual(h.tm.request_stop(t.id), C.REQUESTED)   # honest: step has not unwound yet
        th.join(3)
        self.assertFalse(th.is_alive())
        self.assertEqual((t.state, t.token.state, out[0].ok), (S.CANCELLED, C.STOPPED, False))
        self.assertEqual(h.events(t).count("cancellation_requested"), 1)

    def test_stop_while_waiting_for_approval_discards_the_answer(self):
        gate, entered = threading.Event(), threading.Event()
        h = Harness(decision=D.REQUIRE_APPROVAL, approver=lambda *a: entered.set() or gate.wait(2) or True)
        t = h.tm.create_task("g")
        th = threading.Thread(target=lambda: h.tm.run_step(t.id, "act", {"v": 1}))
        th.start()
        self.assertTrue(entered.wait(2))
        h.tm.request_stop(t.id)
        gate.set()
        th.join(3)
        self.assertEqual((t.state, h.ran), (S.CANCELLED, []))

    def test_duplicate_active_task_prevented(self):
        h = Harness()
        t = h.tm.create_task("g", dedupe_key="k")
        with self.assertRaises(DuplicateTaskError):
            h.tm.create_task("g", dedupe_key="k")
        h.tm.request_stop(t.id)
        h.tm.create_task("g", dedupe_key="k")       # allowed once the first is final


class SessionTests(unittest.TestCase):
    def test_requires_approval_and_enforces_cap(self):
        s = AutomationSession("g", max_runs=3)
        with self.assertRaises(SessionError):
            s.start_run()
        s.approve()
        self.assertEqual([s.start_run() for _ in range(3)], [1, 2, 3])
        with self.assertRaises(SessionError):
            s.start_run()

    def test_stop_on_unexpected_condition(self):
        s = AutomationSession("g")
        s.approve()
        s.start_run()
        s.stop("unexpected screen")
        with self.assertRaises(SessionError):
            s.start_run()

    def test_cap_cannot_exceed_ten(self):
        with self.assertRaises(ValueError):
            AutomationSession("g", max_runs=11)
