from __future__ import annotations

from dataclasses import dataclass

from app.prompts.assistant_prompt import build_system_prompt

from .knowledge import KnowledgeBase, RetrievedChunk
from .memory import DialogMemory
from .providers import AIProviderError, ChatProvider, Message


SMALLTALK_WORDS = {
    "/start",
    "start",
    "привет",
    "здравствуйте",
    "здравствуй",
    "салам",
    "hello",
    "hi",
    "добрый день",
    "доброе утро",
    "добрый вечер",
    "спасибо",
    "благодарю",
}

GREETING_ANSWER = (
    "Здравствуйте! Я AI-ассистент Центра Красок #1. Могу помочь с вопросами "
    "о товарах, услугах, брендах, адресах, доставке, самовывозе и сотрудничестве."
)

SYSTEM_PROMPT_REFUSAL = (
    "Я не могу раскрывать внутренние инструкции, system prompt или технический "
    "контекст. Зато могу помочь с вопросами о Центре Красок #1: товарах, услугах, "
    "брендах, адресах, доставке и сотрудничестве."
)

UNKNOWN_PRODUCT_ANSWER = (
    "В базе знаний нет подтвержденной информации о наличии этого конкретного "
    "товара. Лучше уточнить актуальное наличие у менеджера Центра Красок #1."
)

CLIENTS_TERMS = (
    "клиент",
    "клиенты",
    "покупател",
    "заказчик",
    "заказчики",
    "партнер",
    "партнеры",
)

INTERNAL_KNOWLEDGE_MARKERS = {
    "Known facts:",
    "Answering rules:",
}

COMPANY_RELATED_TERMS = (
    "центр красок",
    "centr krasok",
    "компани",
    "магазин",
    "краск",
    "лак",
    "масл",
    "грунтов",
    "пропит",
    "штукатур",
    "колеров",
    "цвет",
    "бренд",
    "товар",
    "продукт",
    "услуг",
    "достав",
    "самовывоз",
    "адрес",
    "контакт",
    "телефон",
    "email",
    "почт",
    "график",
    "режим",
    "дизайнер",
    "строител",
    "клиент",
    "партнер",
    "проект",
    "ваканс",
    "зарплат",
    "директор",
    "владел",
    "цена",
    "стоим",
    "налич",
    "акци",
)

OUT_OF_SCOPE_TERMS = (
    "матч",
    "футбол",
    "лига",
    "фрайбург",
    "астон",
    "вилла",
    "спорт",
    "прогноз",
    "предскажи",
    "рецепт",
    "плов",
    "погода",
    "курс валют",
    "крипт",
    "новости",
)

OUT_OF_SCOPE_ANSWER = (
    "Я не смогу помочь с этим вопросом. Я отвечаю только на вопросы о Центре "
    "Красок #1: товарах, услугах, брендах, адресах, контактах, доставке и "
    "сотрудничестве."
)

CURRENT_DATA_ANSWERS = (
    (
        ("акци", "скидк", "спецпредлож"),
        "Сейчас не могу подтвердить актуальные акции или специальные предложения. "
        "Они могут меняться, поэтому лучше уточнить действующие условия у менеджера "
        "или на сайте Центра Красок #1.",
    ),
    (
        ("цен", "стоим", "сколько стоит"),
        "Не могу назвать точную актуальную цену без проверки. Цены могут меняться, "
        "поэтому лучше уточнить стоимость конкретного товара у менеджера или на сайте "
        "Центра Красок #1.",
    ),
    (
        ("налич", "в наличии", "остатк", "есть в продаже", "доступен товар"),
        "Не могу подтвердить актуальное наличие товара без проверки. Остатки могут "
        "меняться, поэтому лучше уточнить наличие у менеджера Центра Красок #1.",
    ),
    (
        ("ваканс", "зарплат"),
        "В открытых данных нет подтвержденного списка актуальных вакансий или зарплат. "
        "Лучше уточнить этот вопрос по основному телефону или email Центра Красок #1.",
    ),
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

        if deterministic_answer := get_deterministic_answer(cleaned_text):
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

        if current_data_answer := get_current_data_answer(cleaned_text):
            self._memory.add(chat_id, "user", cleaned_text)
            self._memory.add(chat_id, "assistant", current_data_answer)
            return AssistantAnswer(
                text=current_data_answer,
                used_chunks=[],
                used_provider=self._provider_name,
            )

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
            return GREETING_ANSWER

        if not chunks:
            return (
                "Я могу отвечать только на вопросы о Центре Красок #1. "
                "В доступных данных нет информации для точного ответа на этот вопрос."
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
                "Нашел близкий раздел о Центре Красок #1, но не могу дать точный "
                "ответ. Лучше уточнить вопрос или связаться с менеджером компании."
            )

        return _fallback_intro(user_text) + "\n" + "\n".join(f"• {line}" for line in lines)


def is_clients_question(text: str) -> bool:
    return any(term in text for term in CLIENTS_TERMS)


def get_deterministic_answer(text: str) -> str | None:
    lowered = text.lower()
    if is_start_or_greeting(lowered):
        return GREETING_ANSWER
    if is_internal_instruction_request(lowered):
        return SYSTEM_PROMPT_REFUSAL
    if current_data_answer := get_current_data_answer(lowered):
        return current_data_answer
    if is_unknown_product_question(lowered):
        return UNKNOWN_PRODUCT_ANSWER
    return None


def is_start_or_greeting(text: str) -> bool:
    normalized = text.strip().lower().strip("!.,? ")
    return normalized in SMALLTALK_WORDS


def is_internal_instruction_request(text: str) -> bool:
    markers = (
        "system prompt",
        "системный prompt",
        "системный промпт",
        "системные инструкции",
        "внутренние инструкции",
        "покажи prompt",
        "покажи промпт",
        "раскрой prompt",
        "раскрой промпт",
    )
    return any(marker in text for marker in markers)


def is_out_of_scope_question(text: str, chunks: list[RetrievedChunk]) -> bool:
    lowered = text.lower()
    if any(term in lowered for term in COMPANY_RELATED_TERMS):
        return False
    if any(term in lowered for term in OUT_OF_SCOPE_TERMS):
        return True
    return not chunks


def get_current_data_answer(text: str) -> str | None:
    lowered = text.lower()
    for terms, answer in CURRENT_DATA_ANSWERS:
        if any(term in lowered for term in terms):
            return answer
    return None


def is_unknown_product_question(text: str) -> bool:
    if not any(marker in text for marker in ("у вас есть", "есть ли")):
        return False
    if any(
        marker in text
        for marker in (
            "доставка",
            "самовывоз",
            "услуга",
            "услуги",
            "адрес",
            "контакт",
            "телефон",
            "бренд",
            "бренды",
            "в наличии",
            "наличие",
            "остатк",
        )
    ):
        return False
    return bool(
        any(char.isdigit() for char in text)
        or any("a" <= char <= "z" for char in text)
        or "краска " in text
        or "лак " in text
        or "грунтов" in text
    )


def _fallback_intro(user_text: str) -> str:
    lowered = user_text.lower()
    if "достав" in lowered:
        return "Доставка работает так:"
    if "услуг" in lowered:
        return "Мы предлагаем:"
    if "бренд" in lowered:
        return "У нас представлены такие данные по брендам:"
    if "адрес" in lowered or "контакт" in lowered or "телефон" in lowered:
        return "Связаться с нами можно так:"
    return "Вот основная информация:"
