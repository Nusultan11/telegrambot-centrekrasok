from __future__ import annotations

from typing import Protocol

from .intents import Intent


class ScoredChunk(Protocol):
    title: str


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

INTERNAL_PROMPT_MARKERS = (
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

PRICE_TERMS = (
    "сколько стоит",
    "стоит",
    "цена",
    "цены",
    "стоимость",
    "прайс",
    "ценник",
)

STOCK_TERMS = (
    "в наличии",
    "наличие",
    "остатк",
    "есть в продаже",
    "доступен товар",
)

PROMOTION_TERMS = (
    "акци",
    "скидк",
    "спецпредлож",
)

VACANCY_TERMS = (
    "ваканс",
    "зарплат",
)

COMPANY_OVERVIEW_PATTERNS = (
    "что такое центр красок",
    "что такое цент красок",
    "чем занимается центр красок",
    "чем занимается компания",
    "расскажи о центре красок",
    "расскажите о центре красок",
    "расскажи про центр красок",
    "расскажите про центр красок",
    "расскажи о вашей компании",
    "расскажите о вашей компании",
    "кто вы",
    "о компании",
    "почему стоит обратиться",
    "стоит обратиться",
)

UNKNOWN_PRODUCT_EXCLUSIONS = (
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

CLIENTS_TERMS = (
    "клиент",
    "клиенты",
    "покупател",
    "заказчик",
    "заказчики",
    "партнер",
    "партнеры",
)


def normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()


def detect_intent(text: str) -> Intent:
    normalized = normalize_text(text)
    stripped = normalized.strip("!.,? ")

    if stripped in SMALLTALK_WORDS:
        return Intent.GREETING
    if any(marker in normalized for marker in INTERNAL_PROMPT_MARKERS):
        return Intent.INTERNAL_PROMPT
    if any(pattern in normalized for pattern in COMPANY_OVERVIEW_PATTERNS):
        return Intent.COMPANY_OVERVIEW
    if any(term in normalized for term in PRICE_TERMS):
        return Intent.PRICE
    if any(term in normalized for term in STOCK_TERMS):
        return Intent.STOCK
    if any(term in normalized for term in PROMOTION_TERMS):
        return Intent.PROMOTIONS
    if any(term in normalized for term in VACANCY_TERMS):
        return Intent.VACANCIES
    if is_unknown_product_question(normalized):
        return Intent.UNKNOWN_PRODUCT
    return Intent.GENERAL_RAG


def is_unknown_product_question(text: str) -> bool:
    if not any(marker in text for marker in ("у вас есть", "есть ли")):
        return False
    if any(marker in text for marker in UNKNOWN_PRODUCT_EXCLUSIONS):
        return False
    return bool(
        any(char.isdigit() for char in text)
        or any("a" <= char <= "z" for char in text)
        or "краска " in text
        or "лак " in text
        or "грунтов" in text
    )


def is_clients_question(text: str) -> bool:
    return any(term in normalize_text(text) for term in CLIENTS_TERMS)


def is_out_of_scope_question(text: str, chunks: list[ScoredChunk]) -> bool:
    normalized = normalize_text(text)
    if any(term in normalized for term in COMPANY_RELATED_TERMS):
        return False
    if any(term in normalized for term in OUT_OF_SCOPE_TERMS):
        return True
    return not chunks
