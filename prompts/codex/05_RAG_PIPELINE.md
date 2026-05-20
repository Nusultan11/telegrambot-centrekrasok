Ты работаешь только с RAG pipeline.

Цель RAG:
Не дать LLM отвечать из головы.
Сначала найти релевантный контекст, потом сгенерировать ответ на его основе.

Основные этапы:
1. Load documents
2. Clean text
3. Split into chunks
4. Create embeddings
5. Store vectors
6. Retrieve relevant chunks
7. Build grounded prompt
8. Generate answer
9. Validate answer against context

Правила:
- retrieval должен быть отдельным от generation;
- chunking должен быть настраиваемым;
- top_k должен быть конфигурируемым;
- если контекст не найден, LLM не должен выдумывать;
- ответ должен содержать только информацию из найденного контекста;
- желательно хранить metadata:
  - source;
  - title;
  - url;
  - updated_at;
  - chunk_id.

Минимальные сервисы:
- DocumentLoader
- TextCleaner
- Chunker
- EmbeddingService
- VectorStore
- Retriever
- RagService

Формат ответа:

## Scope
Файлы, с которыми работаешь.

## RAG step
Какой этап RAG улучшается.

## Plan
План.

## Changes
Что изменено.

## Retrieval behavior
Как теперь ищется контекст.

## Hallucination control
Как ограничены ответы без данных.

## How to test
Примеры вопросов для проверки:
- Чем занимается компания?
- Какие услуги предоставляет?
- Где находится офис?
- Какие есть вакансии?
- Что известно о клиентах?

## Commit message
Пример:
feat: add grounded retrieval pipeline for company knowledge
