# MCP-like Tool Contracts

Каждый tool должен иметь явный контракт: имя, ответственность, вход, выход,
ограничения.

## Общие правила

- Один tool делает одну вещь.
- Вход и выход должны быть структурированными.
- Retrieval tool не генерирует финальный ответ.
- Generation tool не ищет данные сам.
- Tool не должен возвращать секреты.
- Tool должен возвращать достаточно metadata для проверки источника.

## search_company_knowledge

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
      "chunk_id": "string",
      "title": "string",
      "text": "string",
      "source": "string",
      "url": "string",
      "score": "float",
      "updated_at": "string"
    }
  ]
}
```

## get_company_contacts

Input:

```json
{
  "city": "string | null"
}
```

Output:

```json
{
  "contacts": [
    {
      "city": "string",
      "address": "string",
      "phone": "string",
      "email": "string | null",
      "working_hours": "string | null",
      "source": "string"
    }
  ]
}
```

## answer_from_context

Input:

```json
{
  "question": "string",
  "context_chunks": [
    {
      "text": "string",
      "source": "string"
    }
  ],
  "language": "string"
}
```

Output:

```json
{
  "answer": "string",
  "grounded": "boolean",
  "missing_information": "string[]"
}
```
