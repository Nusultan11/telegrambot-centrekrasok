from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_BASE = PROJECT_ROOT / "data" / "company_profile.md"


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str | None
    ai_provider: str
    openai_api_key: str | None
    openai_base_url: str | None
    openai_model: str
    amvera_api_token: str | None
    amvera_api_url: str
    amvera_model: str
    knowledge_base_path: Path
    top_k_chunks: int
    max_history_messages: int

    @property
    def resolved_ai_provider(self) -> str:
        provider = self.ai_provider.lower().strip()
        if provider != "auto":
            return provider
        if self.amvera_api_token:
            return "amvera"
        if self.openai_api_key:
            return "openai"
        return "offline"

    @property
    def resolved_model(self) -> str:
        if self.resolved_ai_provider == "amvera":
            return self.amvera_model
        return self.openai_model

    def require_bot_token(self) -> str:
        if not self.telegram_bot_token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is not set. Put it into .env before running the bot."
            )
        return self.telegram_bot_token


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")

    return Settings(
        telegram_bot_token=_optional(os.getenv("TELEGRAM_BOT_TOKEN")),
        ai_provider=os.getenv("AI_PROVIDER", "auto"),
        openai_api_key=_optional(os.getenv("OPENAI_API_KEY")),
        openai_base_url=_optional(os.getenv("OPENAI_BASE_URL")),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        amvera_api_token=_optional(os.getenv("AMVERA_API_TOKEN")),
        amvera_api_url=os.getenv(
            "AMVERA_API_URL", "https://kong-proxy.yc.amvera.ru/api/v1/models/gpt"
        ),
        amvera_model=os.getenv("AMVERA_MODEL", "gpt-5"),
        knowledge_base_path=Path(
            os.getenv("KNOWLEDGE_BASE_PATH", str(DEFAULT_KNOWLEDGE_BASE))
        ),
        top_k_chunks=_int_env("TOP_K_CHUNKS", 5),
        max_history_messages=_int_env("MAX_HISTORY_MESSAGES", 8),
    )
