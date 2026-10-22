import threading
import unittest

from lilyai.agent.cancellation import CancellationState as C, CancellationToken, CancelledError


class CancellationTests(unittest.TestCase):
    def test_request_is_idempotent_and_runs_callbacks_once(self):
        t, calls = CancellationToken(), []
        t.add_callback(lambda: calls.append(1))
        self.assertTrue(t.request("stop"))
        self.assertFalse(t.request("again"))
        self.assertEqual(calls, [1])
        self.assertEqual(t.reason, "stop")

    def test_callback_added_after_cancel_runs_immediately(self):
        t, calls = CancellationToken(), []
        t.request()
        t.add_callback(lambda: calls.append(1))
        self.assertEqual(calls, [1])

    def test_failing_callback_does_not_block_others(self):
        t, calls = CancellationToken(), []
        t.add_callback(lambda: 1 / 0)
        t.add_callback(lambda: calls.append(1))
        t.request()
        self.assertEqual(calls, [1])

    def test_raise_if_cancelled(self):
        t = CancellationToken()
        t.raise_if_cancelled()
        t.request("x")
        with self.assertRaises(CancelledError):
            t.raise_if_cancelled()

    def test_state_progression_and_unresponsive_is_sticky(self):
        t = CancellationToken()
        t.mark_stopped()
        self.assertEqual(t.state, C.NOT_REQUESTED)      # cannot be "stopped" without a request
        t.request()
        t.mark_in_progress()
        self.assertEqual(t.state, C.IN_PROGRESS)
        t.mark_unresponsive()
        t.mark_stopped()
        self.assertEqual(t.state, C.UNRESPONSIVE)

    def test_wait_wakes_on_cancel(self):
        t = CancellationToken()
        threading.Timer(0.05, t.request).start()
        self.assertTrue(t.wait(2))
