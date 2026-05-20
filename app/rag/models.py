from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    title: str
    text: str
    tokens: Counter[str]


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    title: str
    text: str
    score: float


SearchResult = RetrievedChunk
