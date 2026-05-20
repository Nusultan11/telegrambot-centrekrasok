from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from .models import KnowledgeChunk, RetrievedChunk


TOKEN_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9]+")

STOPWORDS = {
    "а",
    "без",
    "бы",
    "в",
    "вам",
    "вас",
    "все",
    "где",
    "для",
    "до",
    "его",
    "если",
    "есть",
    "и",
    "или",
    "из",
    "как",
    "какие",
    "какой",
    "к",
    "ли",
    "на",
    "над",
    "не",
    "о",
    "об",
    "от",
    "по",
    "под",
    "при",
    "про",
    "с",
    "со",
    "так",
    "у",
    "что",
    "чем",
    "это",
    "я",
}

QUERY_EXPANSIONS = {
    "находитесь": ["адрес", "адреса", "контакты", "магазин", "салон", "алматы", "астана"],
    "находится": ["адрес", "адреса", "контакты", "магазин", "салон"],
    "офис": ["адрес", "адреса", "контакты", "магазин", "салон"],
    "адрес": ["контакты", "магазин", "салон"],
    "адреса": ["контакты", "магазин", "салон"],
    "контакты": ["адрес", "адреса", "телефон", "email"],
    "телефон": ["контакты", "адрес"],
    "занимается": ["компания", "профиль", "деятельность", "business", "scope"],
    "деятельность": ["компания", "профиль", "business", "scope"],
    "товары": ["products", "ассортимент", "краски", "лаки", "грунтовки"],
    "товар": ["products", "ассортимент", "краски", "лаки", "грунтовки"],
    "ассортимент": ["products", "товары", "краски", "лаки", "грунтовки"],
    "продаете": ["товары", "products", "ассортимент"],
    "продаёте": ["товары", "products", "ассортимент"],
    "продает": ["товары", "products", "ассортимент"],
    "продаёт": ["товары", "products", "ассортимент"],
    "бренды": ["brands", "dulux", "hammerite", "marshall"],
    "бренд": ["brands", "dulux", "hammerite", "marshall"],
    "представлены": ["brands", "товары", "products"],
    "предлагаете": ["услуги", "services"],
    "дизайнерам": ["designers", "дизайнеры", "проект", "материалы", "услуги"],
    "дизайнеры": ["designers", "дизайнерам", "проект", "материалы", "услуги"],
    "дизайнер": ["designers", "дизайнерам", "проект", "материалы", "услуги"],
    "строителям": ["builders", "contractors", "строители", "строитель", "подрядчики", "бригады", "проекты"],
    "строители": ["builders", "contractors", "строителям", "строитель", "подрядчики", "бригады", "проекты"],
    "строитель": ["builders", "contractors", "строителям", "строители", "подрядчики", "бригады", "проекты"],
    "подрядчикам": ["builders", "contractors", "строители", "строителям", "бригады", "проекты"],
    "подрядчики": ["builders", "contractors", "строители", "строителям", "бригады", "проекты"],
    "бригады": ["строители", "строителям", "подрядчики", "проекты"],
    "цена": ["стоимость", "прайс", "товары", "products", "unknown"],
    "цены": ["стоимость", "прайс", "товары", "products", "unknown"],
    "стоит": ["цена", "стоимость", "прайс", "unknown"],
    "стоимость": ["цена", "прайс", "товары", "products", "unknown"],
    "наличии": ["наличие", "остатки", "товары", "products", "unknown"],
    "наличие": ["остатки", "товары", "products", "unknown"],
    "остатки": ["наличие", "товары", "products", "unknown"],
    "акции": ["скидки", "promotions", "unknown"],
    "акция": ["скидки", "promotions", "unknown"],
    "скидки": ["акции", "promotions", "unknown"],
    "доставка": ["самовывоз", "delivery", "pickup", "адрес", "заказ"],
    "доставки": ["самовывоз", "delivery", "pickup", "адрес", "заказ"],
    "самовывоз": ["доставка", "delivery", "pickup", "шоурум", "магазин"],
    "обратиться": ["компания", "услуги", "преимущества", "консультации"],
    "обращаться": ["компания", "услуги", "преимущества", "консультации"],
    "почему": ["компания", "услуги", "преимущества", "консультации"],
}


def tokenize(text: str) -> list[str]:
    tokens = []
    for match in TOKEN_RE.finditer(text.lower()):
        token = match.group(0).replace("ё", "е")
        if len(token) <= 1 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def expand_query_tokens(tokens: list[str]) -> list[str]:
    expanded = list(tokens)
    for token in tokens:
        expanded.extend(QUERY_EXPANSIONS.get(token, []))
    return expanded


def _split_markdown_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "Общие сведения"
    current_lines: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = line.replace("#", "").strip()
            current_lines = [line]
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    return [
        (title, "\n".join(lines).strip())
        for title, lines in sections
        if "\n".join(lines).strip()
    ]


class KnowledgeBase:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self._chunks = chunks
        self._doc_freq = self._build_doc_freq(chunks)

    @classmethod
    def from_markdown(cls, path: Path) -> "KnowledgeBase":
        markdown = path.read_text(encoding="utf-8")
        chunks = []
        for title, text in _split_markdown_sections(markdown):
            chunk_tokens = Counter(tokenize(f"{title}\n{text}"))
            if chunk_tokens:
                chunks.append(KnowledgeChunk(title=title, text=text, tokens=chunk_tokens))
        return cls(chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_tokens = expand_query_tokens(tokenize(query))
        if not query_tokens:
            return []

        query_counts = Counter(query_tokens)
        scored: list[RetrievedChunk] = []
        for chunk in self._chunks:
            score = self._score(query_counts, chunk)
            if score > 0:
                scored.append(
                    RetrievedChunk(title=chunk.title, text=chunk.text, score=score)
                )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _build_doc_freq(chunks: list[KnowledgeChunk]) -> Counter[str]:
        doc_freq: Counter[str] = Counter()
        for chunk in chunks:
            doc_freq.update(chunk.tokens.keys())
        return doc_freq

    def _score(self, query_counts: Counter[str], chunk: KnowledgeChunk) -> float:
        score = 0.0
        doc_count = max(len(self._chunks), 1)
        title_tokens = set(tokenize(chunk.title))
        for token, query_count in query_counts.items():
            term_freq = chunk.tokens.get(token, 0)
            if term_freq == 0:
                continue
            idf = math.log((doc_count + 1) / (self._doc_freq[token] + 1)) + 1
            title_boost = 1.7 if token in title_tokens else 1.0
            score += query_count * (1 + math.log(term_freq)) * idf * title_boost
        return score
