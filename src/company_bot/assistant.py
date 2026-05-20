from __future__ import annotations

from dataclasses import dataclass

from app.policies.answer_policy import (
    CLIENTS_FALLBACK_ANSWER,
    GREETING_ANSWER,
    OUT_OF_SCOPE_ANSWER,
    build_deterministic_answer,
)
from app.policies.voice import apply_company_voice
from app.prompts.assistant_prompt import build_system_prompt
from app.router.router import (
    detect_intent,
    is_clients_question,
    is_out_of_scope_question,
)

from .knowledge import KnowledgeBase, RetrievedChunk
from .memory import DialogMemory
from .providers import AIProviderError, ChatProvider, Message


INTERNAL_KNOWLEDGE_MARKERS = {
    "Known facts:",
    "Answering rules:",
}


@dataclass(frozen=True, slots=True)
class AssistantAnswer:
    text: str
    used_chunks: list[RetrievedChunk]
    used_provider: str


class CompanyAssistant:
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        provider: ChatProvider,
        memory: DialogMemory,
        top_k_chunks: int = 5,
        provider_name: str = "unknown",
    ) -> None:
        self._knowledge_base = knowledge_base
        self._provider = provider
        self._memory = memory
        self._top_k_chunks = top_k_chunks
        self._provider_name = provider_name

    async def answer(self, chat_id: int, user_text: str) -> AssistantAnswer:
        cleaned_text = " ".join(user_text.split())
        if not cleaned_text:
            return AssistantAnswer(
                text="Напишите вопрос о Центре Красок #1, и я помогу сориентироваться по нашим товарам, услугам, адресам или доставке.",
                used_chunks=[],
                used_provider=self._provider_name,
            )

        intent = detect_intent(cleaned_text)
        if deterministic_answer := build_deterministic_answer(intent, cleaned_text):
            self._memory.add(chat_id, "user", cleaned_text)
            self._memory.add(chat_id, "assistant", deterministic_answer)
            return AssistantAnswer(
                text=deterministic_answer,
                used_chunks=[],
                used_provider="local",
            )

        chunks = self._knowledge_base.search(cleaned_text, top_k=self._top_k_chunks)
        if is_out_of_scope_question(cleaned_text, chunks):
            self._memory.add(chat_id, "user", cleaned_text)
            self._memory.add(chat_id, "assistant", OUT_OF_SCOPE_ANSWER)
            return AssistantAnswer(
                text=OUT_OF_SCOPE_ANSWER,
                used_chunks=[],
                used_provider=self._provider_name,
            )

        messages = self._build_messages(chat_id, cleaned_text, chunks)

        try:
            answer_text = await self._provider.generate(messages)
        except AIProviderError:
            answer_text = self._fallback_answer(cleaned_text, chunks)

        answer_text = apply_company_voice(answer_text)
        self._memory.add(chat_id, "user", cleaned_text)
        self._memory.add(chat_id, "assistant", answer_text)
        return AssistantAnswer(
            text=answer_text,
            used_chunks=chunks,
            used_provider=self._provider_name,
        )

    def _build_messages(
        self, chat_id: int, user_text: str, chunks: list[RetrievedChunk]
    ) -> list[Message]:
        context = self._format_context(chunks)
        messages: list[Message] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "system", "content": context},
        ]
        messages.extend(self._memory.get(chat_id))
        messages.append({"role": "user", "content": user_text})
        return messages

    @staticmethod
    def _format_context(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "Контекст компании: релевантные факты не найдены."

        parts = ["Контекст компании:"]
        for index, chunk in enumerate(chunks, start=1):
            parts.append(f"[{index}] {chunk.title}\n{chunk.text}")
        return "\n\n".join(parts)

    @staticmethod
    def _fallback_answer(user_text: str, chunks: list[RetrievedChunk]) -> str:
        lowered = user_text.lower()
        if not chunks:
            return (
                "Я могу отвечать только на вопросы о Центре Красок #1. "
                "Сейчас я не могу дать точный ответ по этому вопросу."
            )

        if is_clients_question(lowered):
            return CLIENTS_FALLBACK_ANSWER

        lines: list[str] = []
        for chunk in chunks[:2]:
            if chunk.title in {"14. Answering Restrictions", "15. Unknown Information"}:
                continue
            for raw_line in chunk.text.splitlines():
                line = raw_line.strip(" -")
                if line == "Answering rules:":
                    break
                if (
                    not line
                    or line in INTERNAL_KNOWLEDGE_MARKERS
                    or line.startswith("#")
                    or line.startswith("Дата подготовки")
                    or line.startswith("Основные источники")
                    or line.startswith("Назначение файла")
                ):
                    continue
                lines.append(line)
                if len(lines) >= 10:
                    break
            if len(lines) >= 10:
                break

        if not lines:
            return (
                "Сейчас я не могу дать точный ответ по этому вопросу. Вы можете "
                "уточнить детали у нашего менеджера Центра Красок #1."
            )

        return _fallback_intro(user_text) + "\n" + "\n".join(f"• {line}" for line in lines)


def _fallback_intro(user_text: str) -> str:
    lowered = user_text.lower()
    if "достав" in lowered:
        return "Доставка работает так:"
    if "услуг" in lowered:
        return "Мы предлагаем:"
    if "бренд" in lowered:
        return "У нас представлены такие бренды:"
    if "адрес" in lowered or "контакт" in lowered or "телефон" in lowered:
        return "Связаться с нами можно так:"
    return "Вот основная информация:"
