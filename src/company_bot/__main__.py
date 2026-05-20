from __future__ import annotations

import logging

from .assistant import CompanyAssistant
from .bot import run
from .config import load_settings
from .knowledge import KnowledgeBase
from .memory import DialogMemory
from .providers import create_provider


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = load_settings()
    knowledge_base = KnowledgeBase.from_markdown(settings.knowledge_base_path)
    provider = create_provider(settings)
    memory = DialogMemory(max_messages=settings.max_history_messages)
    assistant = CompanyAssistant(
        knowledge_base=knowledge_base,
        provider=provider,
        memory=memory,
        top_k_chunks=settings.top_k_chunks,
        provider_name=settings.resolved_ai_provider,
    )
    run(settings.require_bot_token(), assistant)


if __name__ == "__main__":
    main()
