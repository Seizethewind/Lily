"""Tool registry with argument validation (notes sections 11, 15)."""
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Tuple


class ToolError(Exception):
    pass


class UnknownToolError(ToolError):
    pass


class ToolArgumentError(ToolError):
    pass


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    params: Mapping[str, type]
    run: Callable[[dict, Any], Any]          # run(args, cancellation_token)
    required: Tuple[str, ...] = ()


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool):
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name):
        try:
            return self._tools[name]
        except KeyError:
            raise UnknownToolError(f"unknown tool: {name}") from None

    def names(self):
        return sorted(self._tools)

    def validate(self, name, args):
        tool = self.get(name)
        if not isinstance(args, dict):
            raise ToolArgumentError("arguments must be an object")
        for key in args:
            if key not in tool.params:
                raise ToolArgumentError(f"unexpected argument: {key}")
        for key in tool.required:
            if key not in args:
                raise ToolArgumentError(f"missing argument: {key}")
        for key, value in args.items():
            expected = tool.params[key]
            wrong_bool = isinstance(value, bool) and expected is not bool
            if wrong_bool or not isinstance(value, expected):
                raise ToolArgumentError(f"argument {key} must be {expected.__name__}")
