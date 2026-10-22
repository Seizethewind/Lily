"""Secret redaction for logs and error messages (notes sections 8, 12)."""
import re

_TAVILY = re.compile(r"tvly-[A-Za-z0-9_\-]+")
_ASSIGNMENT = re.compile(r"(?i)(api[_-]?key|token|password|secret)(\s*[=:]\s*)\S+")
_BEARER = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+")


def redact(text, secrets=()):
    """Return text with known secrets and common credential patterns removed."""
    if not text:
        return text
    out = str(text)
    for secret in secrets:
        if secret:
            out = out.replace(secret, "[REDACTED]")
    out = _TAVILY.sub("[REDACTED]", out)
    out = _ASSIGNMENT.sub(lambda m: m.group(1) + m.group(2) + "[REDACTED]", out)
    out = _BEARER.sub(lambda m: m.group(1) + "[REDACTED]", out)
    return out
