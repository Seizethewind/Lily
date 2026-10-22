import unittest

from lilyai.memory.approved_memory import MemoryManager, MemoryProposalError
from lilyai.memory.local_store import LocalStore


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = LocalStore()
        self.mem = MemoryManager(self.store)

    def test_proposed_memory_is_not_approved_knowledge(self):
        self.mem.propose("fact", "Owner uses an OPPO A92")
        self.assertEqual(self.mem.list("approved"), [])
        self.assertEqual(len(self.mem.list("proposed")), 1)

    def test_approve_and_sync_candidates(self):
        mid, created = self.mem.propose("procedure", "Open settings, then Apps")
        self.assertTrue(created)
        self.mem.approve(mid)
        self.assertEqual([m["id"] for m in self.mem.sync_candidates()], [mid])

    def test_duplicates_are_prevented_ignoring_case_and_whitespace(self):
        a, _ = self.mem.propose("fact", "Hello   World")
        b, created = self.mem.propose("fact", " hello world ")
        self.assertEqual(a, b)
        self.assertFalse(created)

    def test_rejected_memory_is_never_silently_resurrected(self):
        mid, _ = self.mem.propose("fact", "x y z")
        self.mem.reject(mid)
        again, created = self.mem.propose("fact", "x y z")
        self.assertEqual((again, created), (mid, False))
        self.assertEqual(self.mem.list("approved"), [])
        with self.assertRaises(MemoryProposalError):
            self.mem.approve(mid)

    def test_validation(self):
        with self.assertRaises(MemoryProposalError):
            self.mem.propose("gossip", "x")
        with self.assertRaises(MemoryProposalError):
            self.mem.propose("fact", "   ")

    def test_conversation_history_is_separate_from_memory(self):
        self.store.add_message("c1", "user", "hi")
        self.store.add_message("c1", "assistant", "hello")
        self.assertEqual([m["role"] for m in self.store.recent_messages("c1")], ["user", "assistant"])
        self.assertEqual(self.mem.list("proposed"), [])

    def test_settings_round_trip_and_persistence(self):
        import os, tempfile
        path = os.path.join(tempfile.mkdtemp(), "lily.db")
        s = LocalStore(path)
        s.set_setting("bubble_opacity", 0.8)
        s.set_setting("bubble_opacity", 0.5)
        s.close()
        self.assertEqual(LocalStore(path).get_setting("bubble_opacity"), "0.5")
        self.assertEqual(LocalStore(path).get_setting("missing", "d"), "d")
