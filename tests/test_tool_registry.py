import unittest

from lilyai.llm.engine import EchoEngine, ModelNotLoaded
from lilyai.tools.registry import Tool, ToolArgumentError, ToolRegistry, UnknownToolError


def tool():
    return Tool("t", "d", {"q": str, "n": int}, lambda a, t: a, required=("q",))


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.r = ToolRegistry()
        self.r.register(tool())

    def test_valid_args(self):
        self.r.validate("t", {"q": "x", "n": 2})

    def test_rejects_bad_args(self):
        for args in ({}, {"q": "x", "zzz": 1}, {"q": 5}, {"q": "x", "n": True}, "nope"):
            with self.assertRaises(ToolArgumentError, msg=args):
                self.r.validate("t", args)

    def test_unknown_and_duplicate(self):
        with self.assertRaises(UnknownToolError):
            self.r.get("missing")
        with self.assertRaises(ValueError):
            self.r.register(tool())

    def test_engine_interface_requires_load(self):
        e = EchoEngine()
        with self.assertRaises(ModelNotLoaded):
            e.generate("hi")
        e.load()
        self.assertEqual(e.generate("hi"), "hi")
