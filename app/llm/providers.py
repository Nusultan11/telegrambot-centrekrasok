from __future__ import annotations

import json
from typing import Any

from app.core.config import Settings

from .base import AIProviderError, ChatProvider, Message


class OpenAIChatProvider(ChatProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def generate(self, messages: list[Message]) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.2,
                max_tokens=900,
            )
            content = response.choices[0].message.content
        except Exception as exc:  # pragma: no cover - network/provider branch
            raise AIProviderError(str(exc)) from exc
        if not content:
            raise AIProviderError("AI provider returned an empty response.")
        return content.strip()


class AmveraChatProvider(ChatProvider):
    def __init__(self, api_token: str, model: str, api_url: str) -> None:
        self._api_token = api_token
        self._model = model
        self._api_url = api_url

    async def generate(self, messages: list[Message]) -> str:
        import aiohttp

        payload = {
            "model": self._model,
            "messages": [
                {"role": message["role"], "text": message["content"]}
                for message in messages
            ],
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": f"Bearer {self._api_token}",
        }
        try:
            timeout = aiohttp.ClientTimeout(total=45)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self._api_url, headers=headers, json=payload
                ) as response:
                    body = await response.text()
                    if response.status >= 400:
                        raise AIProviderError(
                            f"Amvera API returned HTTP {response.status}: {body[:300]}"
                        )
        except AIProviderError:
            raise
        except Exception as exc:  # pragma: no cover - network/provider branch
            raise AIProviderError(str(exc)) from exc

        return self._extract_text(body)

    @staticmethod
    def _extract_text(body: str) -> str:
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise AIProviderError("Amvera API returned invalid JSON.") from exc

        text = _find_text(data)
        if not text:
            raise AIProviderError("Amvera API returned no text content.")
        return text.strip()


class OfflineFactProvider(ChatProvider):
    async def generate(self, messages: list[Message]) -> str:
        context_message = next(
            (
                message["content"]
                for message in messages
                if message["role"] == "system"
                and message["content"].startswith("Контекст компании:")
            ),
            "",
        )
        if not context_message:
            return (
                "Я могу отвечать только по базе знаний о Центре Красок #1. "
                "В доступных данных нет информации для ответа на этот вопрос."
            )

        facts = []
        for line in context_message.splitlines():
            clean = line.strip(" -")
            if clean and not clean.startswith(
                ("Контекст", "[", "##", "Дата подготовки", "Основные источники")
            ):
                facts.append(clean)
            if len(facts) >= 8:
                break

        if not facts:
            return (
                "В базе знаний есть близкая информация, но ее недостаточно для "
                "точного ответа. Лучше уточнить вопрос или связаться с менеджером "
                "Центра Красок #1."
            )
        return "По базе знаний Центра Красок #1:\n" + "\n".join(
            f"- {fact}" for fact in facts
        )


def create_provider(settings: Settings) -> ChatProvider:
    provider = settings.resolved_ai_provider
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for AI_PROVIDER=openai.")
        return OpenAIChatProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
        )
    if provider == "amvera":
        if not settings.amvera_api_token:
            raise RuntimeError("AMVERA_API_TOKEN is required for AI_PROVIDER=amvera.")
        return AmveraChatProvider(
            api_token=settings.amvera_api_token,
            model=settings.amvera_model,
            api_url=settings.amvera_api_url,
        )
    if provider in {"offline", "none"}:
        return OfflineFactProvider()
    raise RuntimeError(
        "Unsupported AI_PROVIDER. Use auto, openai, amvera, offline, or none."
    )


def _find_text(data: Any) -> str | None:
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ("content", "text", "answer", "response", "message"):
            value = data.get(key)
            found = _find_text(value)
            if found:
                return found
        choices = data.get("choices")
        found = _find_text(choices)
        if found:
            return found
    if isinstance(data, list):
        for item in data:
            found = _find_text(item)
            if found:
                return found
    return None
