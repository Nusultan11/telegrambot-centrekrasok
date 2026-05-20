# MCP-like Resource Metadata

Любой фрагмент базы знаний должен быть пригоден для проверки и обновления.

## Минимальная metadata

```json
{
  "chunk_id": "string",
  "title": "string",
  "source": "string",
  "url": "string",
  "updated_at": "YYYY-MM-DD",
  "content_type": "company_profile | contacts | services | products | social | vacancies",
  "confidence": "high | medium | low"
}
```

## Правила

- Не смешивать текст и metadata в одном неструктурированном поле, если задача
  требует machine-readable output.
- Для данных, которые могут устареть, указывать `updated_at`.
- Для неподтверждённых данных использовать `confidence: low` или не включать их
  в ответы.
- Если источник неизвестен, лучше не использовать факт в grounded answer.

## Почему это важно

Metadata помогает:

- объяснить, откуда взят ответ;
- обновлять устаревшие данные;
- тестировать retrieval;
- ограничивать галлюцинации;
- строить future MCP/tools API.
