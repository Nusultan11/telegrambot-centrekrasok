from __future__ import annotations

from dataclasses import dataclass

from app.prompts.assistant_prompt import build_system_prompt

from .knowledge import KnowledgeBase, RetrievedChunk
from .memory import DialogMemory
from .providers import AIProviderError, ChatProvider, Message


SMALLTALK_WORDS = {
    "привет",
    "здравствуйте",
    "салам",
    "hello",
    "hi",
    "спасибо",
    "благодарю",
}

CLIENTS_TERMS = (
    "клиент",
    "клиенты",
    "покупател",
    "заказчик",
    "заказчики",
    "партнер",
    "партнеры",
)

CLIENTS_FALLBACK_ANSWER = """
Компания "Центр Красок #1" работает с широким кругом клиентов, включая:

• Частных клиентов: люди, которые хотят обновить свои дома, квартиры, мебель, фасады или другие личные пространства.
• Дизайнеров: профессионалы, которые используют продукцию компании в дизайн-проектах и подбирают материалы, цвета и декоративные решения для клиентов.
• Строителей: компании и бригады, занимающиеся строительством, ремонтом и отделочными работами.
• Проектных заказчиков: организации и компании, реализующие крупные строительные или ремонтные проекты.

Компания также упоминает сотни реализованных проектов и более 200 лояльных партнеров. Эти данные стоит воспринимать как информацию с сайта компании, но они хорошо показывают, что Центр Красок #1 работает не только с частными покупателями, но и с профессиональным проектным сегментом.
""".strip()


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
                text="Напишите вопрос о Центре Красок #1, и я отвечу по данным компании.",
                used_chunks=[],
                used_provider=self._provider_name,
            )

        chunks = self._knowledge_base.search(cleaned_text, top_k=self._top_k_chunks)
        messages = self._build_messages(chat_id, cleaned_text, chunks)

        try:
            answer_text = await self._provider.generate(messages)
        except AIProviderError:
            answer_text = self._fallback_answer(cleaned_text, chunks)

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
        if any(word in lowered for word in SMALLTALK_WORDS):
            return (
                "Здравствуйте. Я помогу с вопросами о Центре Красок #1: товарах, "
                "услугах, адресах, брендах, доставке и сотрудничестве."
            )

        if not chunks:
            return (
                "Я могу отвечать только на вопросы о Центре Красок #1. "
                "В доступных данных нет информации для точного ответа на этот вопрос."
            )

        if is_clients_question(lowered):
            return CLIENTS_FALLBACK_ANSWER

        lines: list[str] = []
        for chunk in chunks[:2]:
            for raw_line in chunk.text.splitlines():
                line = raw_line.strip(" -")
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("Дата подготовки")
                    or line.startswith("Основные источники")
                ):
                    continue
                lines.append(line)
                if len(lines) >= 10:
                    break
            if len(lines) >= 10:
                break

        if not lines:
            return (
                "Нашел близкий раздел о Центре Красок #1, но не могу дать точный "
                "ответ. Лучше уточнить вопрос или связаться с менеджером компании."
            )

        return "По данным компании:\n" + "\n".join(f"- {line}" for line in lines)


def is_clients_question(text: str) -> bool:
    return any(term in text for term in CLIENTS_TERMS)
