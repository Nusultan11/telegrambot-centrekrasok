# MCP-like Architecture Overview

Используй эту папку как источник правил для задач, где нужно проектировать
tools/resources, контракты источников данных или разделение retrieval и
generation.

## Главная идея

AI-ассистент не должен "знать всё сам". Он должен получать контекст через
явные ресурсы и инструменты:

- `search_company_knowledge`
- `get_company_contacts`
- `get_company_services`
- `get_relevant_context`
- `answer_from_context`

## Принцип разделения

- Tool для retrieval только ищет данные и возвращает структурированный context.
- Tool для generation только формирует ответ по уже переданному context.
- Source/resource хранит metadata: `source`, `url`, `title`, `updated_at`,
  `chunk_id`.
- LLM не должна сама решать, где искать данные, если есть отдельный tool.

## Когда применять

Опирайся на эти инструкции, если задача связана с:

- RAG;
- knowledge base;
- metadata;
- источниками данных;
- tool contracts;
- MCP-like архитектурой;
- hallucination control;
- разделением LLM и внешних данных.
