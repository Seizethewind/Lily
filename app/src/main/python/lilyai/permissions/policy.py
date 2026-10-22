"""Permission policy enforced by the execution system, not by the model (notes sections 4F, 10, 20).

PROVISIONAL: the exact terminal permission tiers (Topic 23 Decision 3) are NOT VERIFIED.
The tiers below are a conservative placeholder and must be reviewed by the project owner.
"""
import os
import shlex
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str


TERMINAL_TOOL = "terminal.command"
_SHELL_OPERATORS = set(";&|<>`$\n")
_ROOT = {"su", "sudo", "doas"}
_SENSITIVE = {
    "rm", "rmdir", "mv", "dd", "mkfs", "chmod", "chown", "kill", "killall", "pkill",
    "pm", "am", "settings", "svc", "reboot", "shutdown", "mount", "umount",
    "curl", "wget", "nc", "ssh", "scp", "pip", "pip3",
}
_SAFE = {"pwd", "ls", "echo", "date", "whoami", "uname", "id"}


def classify_command(command):
    if not isinstance(command, str) or not command.strip():
        return PolicyResult(Decision.DENY, "empty or invalid command")
    if _SHELL_OPERATORS & set(command):
        return PolicyResult(Decision.DENY, "shell operators are not permitted; submit one command at a time")
    try:
        argv = shlex.split(command)
    except ValueError:
        return PolicyResult(Decision.DENY, "command could not be parsed")
    if not argv:
        return PolicyResult(Decision.DENY, "empty command")
    program = os.path.basename(argv[0]).lower()
    if program in _ROOT:
        return PolicyResult(Decision.DENY, "root access is not assumed or provided")
    if program in _SENSITIVE:
        return PolicyResult(Decision.REQUIRE_APPROVAL, f"{program} is destructive or security-sensitive")
    if program in _SAFE:
        return PolicyResult(Decision.ALLOW, f"{program} is a harmless read-only command")
    return PolicyResult(Decision.REQUIRE_APPROVAL, f"{program} is not on the automatic allow list")


class PermissionPolicy:
    """Unknown tools default to REQUIRE_APPROVAL (supervised mode)."""

    def __init__(self, tool_rules=None, default=Decision.REQUIRE_APPROVAL):
        self._rules = dict(tool_rules or {})
        self._default = default

    def evaluate(self, tool_name, args):
        if tool_name == TERMINAL_TOOL:
            return classify_command(args.get("command"))
        decision = self._rules.get(tool_name, self._default)
        return PolicyResult(decision, f"policy rule for {tool_name}")
