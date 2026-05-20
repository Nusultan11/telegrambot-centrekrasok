Ты работаешь с источниками и MCP-like подходом.

Перед выполнением MCP-like задач опирайся на дополнительные инструкции:

- `prompts/codex/mcp/00_MCP_OVERVIEW.md`
- `prompts/codex/mcp/01_TOOL_CONTRACTS.md`
- `prompts/codex/mcp/02_RESOURCE_METADATA.md`
- `prompts/codex/mcp/03_MCP_TASK_PROMPT.md`

Контекст:
Проект можно мыслить как MCP-like систему:
AI-ассистент не должен знать всё сам.
Он должен обращаться к инструментам и ресурсам:
- search_company_knowledge;
- get_company_contacts;
- get_company_services;
- get_relevant_context;
- answer_from_context.

Цель:
Разделить LLM и источники данных.

Правила:
- tools/resources должны иметь явные входы и выходы;
- каждый tool должен делать одну вещь;
- retrieval tool не должен генерировать финальный ответ;
- generation tool не должен сам искать данные;
- источники должны иметь metadata;
- ответы tools должны быть структурированными.

Пример tool schema:

Tool:
search_company_knowledge

Input:
```json
{
  "query": "string",
  "top_k": "integer"
}
```

Output:
```json
{
  "chunks": [
    {
      "text": "string",
      "source": "string",
      "url": "string",
      "score": "float"
    }
  ]
}
```

Формат ответа:

## Scope
Файлы.

## MCP-like resource/tool
Что создаём или улучшаем.

## Plan
План.

## Changes
Изменения.

## Tool contract
Вход/выход.

## Why it matters
Зачем это нужно для AI assistant.

## Commit message
Пример:
feat: add company knowledge search tool contract
