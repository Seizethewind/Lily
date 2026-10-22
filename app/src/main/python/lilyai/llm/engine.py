"""Stable interface to local inference (notes sections 7, 16).

No real engine is integrated yet: the runtime and model are NOT VERIFIED and need on-device tests (Milestone 3).
"""
from abc import ABC, abstractmethod


class EngineError(Exception):
    pass


class ModelNotLoaded(EngineError):
    pass


class LLMEngine(ABC):
    @property
    @abstractmethod
    def is_loaded(self): ...

    @abstractmethod
    def load(self): ...

    @abstractmethod
    def unload(self): ...

    @abstractmethod
    def generate(self, prompt, *, token=None, max_tokens=256): ...


class EchoEngine(LLMEngine):
    """Test double. Not a model."""

    def __init__(self):
        self._loaded = False

    @property
    def is_loaded(self):
        return self._loaded

    def load(self):
        self._loaded = True

    def unload(self):
        self._loaded = False

    def generate(self, prompt, *, token=None, max_tokens=256):
        if not self._loaded:
            raise ModelNotLoaded("model is not loaded")
        if token is not None:
            token.raise_if_cancelled()
        return prompt[:max_tokens]
