"""Intent routing for the hybrid RAG assistant."""

from .intents import Intent
from .router import detect_intent, normalize_text

__all__ = ["Intent", "detect_intent", "normalize_text"]
