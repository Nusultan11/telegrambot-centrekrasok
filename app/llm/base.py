from __future__ import annotations

from abc import ABC, abstractmethod


Message = dict[str, str]


class AIProviderError(RuntimeError):
    """Raised when the configured AI provider cannot return an answer."""


class ChatProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list[Message]) -> str:
        raise NotImplementedError
