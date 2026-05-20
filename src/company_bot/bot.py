from __future__ import annotations

import asyncio
import html
import logging
import re

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatAction, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from .assistant import CompanyAssistant


LOGGER = logging.getLogger(__name__)
MAX_TELEGRAM_MESSAGE = 3900


def build_dispatcher(assistant: CompanyAssistant) -> Dispatcher:
    router = Router()

    @router.message(F.text)
    async def handle_text(message: Message, bot: Bot) -> None:
        if not message.text:
            return
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        answer = await assistant.answer(message.chat.id, message.text)
        for part in split_message(answer.text):
            await send_formatted_message(message, part)

    @router.message()
    async def handle_non_text(message: Message) -> None:
        await message.answer(
            "Пока я отвечаю только на текстовые вопросы о Центре Красок #1."
        )

    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    return dispatcher


async def run_bot(token: str, assistant: CompanyAssistant) -> None:
    bot = Bot(token=token)
    dispatcher = build_dispatcher(assistant)
    LOGGER.info("Bot polling started")
    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


def split_message(text: str) -> list[str]:
    if len(text) <= MAX_TELEGRAM_MESSAGE:
        return [text]

    parts: list[str] = []
    remaining = text
    while len(remaining) > MAX_TELEGRAM_MESSAGE:
        split_at = remaining.rfind("\n", 0, MAX_TELEGRAM_MESSAGE)
        if split_at == -1:
            split_at = MAX_TELEGRAM_MESSAGE
        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts


async def send_formatted_message(message: Message, text: str) -> None:
    formatted_text = format_telegram_html(text)
    try:
        await message.answer(formatted_text, parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await message.answer(strip_html(formatted_text))


def format_telegram_html(text: str) -> str:
    bold_open = "\uE000"
    bold_close = "\uE001"
    normalized = (
        text.strip()
        .replace("<strong>", bold_open)
        .replace("</strong>", bold_close)
        .replace("<b>", bold_open)
        .replace("</b>", bold_close)
    )

    lines = []
    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue

        heading = re.match(r"^#{1,6}\s+(.+)$", line)
        if heading:
            lines.append(f"<b>{html.escape(heading.group(1), quote=False)}</b>")
            continue

        bullet = re.match(r"^(?:[-*]|•)\s+(.+)$", line)
        prefix = "• " if bullet else ""
        content = bullet.group(1).strip() if bullet else line
        escaped = html.escape(content, quote=False)
        escaped = _convert_bold_markdown(escaped)
        escaped = escaped.replace(bold_open, "<b>").replace(bold_close, "</b>")
        lines.append(prefix + escaped)

    return "\n".join(lines).strip()


def _convert_bold_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    return text


def strip_html(text: str) -> str:
    without_tags = re.sub(r"</?b>", "", text)
    return html.unescape(without_tags)


def run(token: str, assistant: CompanyAssistant) -> None:
    asyncio.run(run_bot(token, assistant))
