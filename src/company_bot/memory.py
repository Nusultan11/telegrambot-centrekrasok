from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque


ChatMessage = dict[str, str]


class DialogMemory:
    def __init__(self, max_messages: int = 8) -> None:
        self._messages: defaultdict[int, Deque[ChatMessage]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def add(self, chat_id: int, role: str, content: str) -> None:
        self._messages[chat_id].append({"role": role, "content": content})

    def get(self, chat_id: int) -> list[ChatMessage]:
        return list(self._messages[chat_id])

    def clear(self, chat_id: int) -> None:
        self._messages.pop(chat_id, None)
