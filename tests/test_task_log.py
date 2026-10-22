import unittest

from lilyai.history.task_log import TaskLog
from lilyai.utils.logging_utils import redact


class TaskLogTests(unittest.TestCase):
    def test_records_and_filters_by_task(self):
        log = TaskLog()
        log.record("a", "task_created", state="CREATED")
        log.record("b", "task_created")
        log.record("a", "tool_started", tool="web.search", approval="granted")
        events = log.events("a")
        self.assertEqual([e["event_type"] for e in events], ["task_created", "tool_started"])
        self.assertEqual(events[1]["tool"], "web.search")
        self.assertEqual(len(log.events()), 3)

    def test_secrets_are_redacted(self):
        log = TaskLog(secrets=["hunter2"])
        log.record("a", "action_failed", error_message="bad key hunter2 and tvly-abc123", summary="api_key=zzz")
        e = log.events("a")[0]
        for field in ("error_message", "summary"):
            for leaked in ("hunter2", "tvly-abc123", "zzz"):
                self.assertNotIn(leaked, e[field])

    def test_redact_patterns(self):
        self.assertNotIn("abc", redact("Authorization: Bearer abc.def"))
        self.assertEqual(redact("max_tokens: 5"), "max_tokens: 5")
        self.assertIsNone(redact(None))
