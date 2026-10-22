import unittest

from lilyai.permissions.policy import Decision as D, PermissionPolicy, classify_command


class PolicyTests(unittest.TestCase):
    def test_harmless_commands_allowed(self):
        for cmd in ("pwd", "ls -la", "echo hello"):
            self.assertEqual(classify_command(cmd).decision, D.ALLOW, cmd)

    def test_sensitive_and_unknown_commands_need_approval(self):
        for cmd in ("rm -rf data", "chmod 777 x", "curl http://example.com", "somethingelse"):
            self.assertEqual(classify_command(cmd).decision, D.REQUIRE_APPROVAL, cmd)

    def test_root_and_shell_chaining_denied(self):
        for cmd in ("su", "sudo ls", "ls; rm -rf /", "echo a | sh", "echo $(id)", "ls > f", ""):
            self.assertEqual(classify_command(cmd).decision, D.DENY, cmd)

    def test_path_prefix_does_not_bypass_classification(self):
        self.assertEqual(classify_command("/system/bin/rm x").decision, D.REQUIRE_APPROVAL)

    def test_unknown_tool_defaults_to_approval(self):
        self.assertEqual(PermissionPolicy().evaluate("anything", {}).decision, D.REQUIRE_APPROVAL)

    def test_explicit_rule_and_terminal_routing(self):
        p = PermissionPolicy({"web.search": D.ALLOW})
        self.assertEqual(p.evaluate("web.search", {}).decision, D.ALLOW)
        self.assertEqual(p.evaluate("terminal.command", {"command": "sudo x"}).decision, D.DENY)
