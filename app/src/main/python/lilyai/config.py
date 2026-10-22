"""Central configuration constants (notes sections 3, 4F, 11)."""
from dataclasses import dataclass

GIB = 1024 ** 3


@dataclass(frozen=True)
class Config:
    supervised: bool = True                      # supervised mode is the default
    max_runs_per_session: int = 10               # session-level cap, not a license to loop
    ai_storage_limit_bytes: int = 30 * GIB       # ceiling for AI data, not a target
    script_timeout_seconds: float = 30.0
    output_limit_chars: int = 64 * 1024


DEFAULT_CONFIG = Config()
