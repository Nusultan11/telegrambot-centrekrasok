Контекст проекта:

Мы делаем Telegram-бота с AI-ассистентом для компании Centr Krasok.

Бот должен:
- принимать обычные сообщения пользователя;
- понимать вопрос;
- искать релевантную информацию в базе знаний компании;
- передавать найденный контекст в LLM;
- отвечать только на основе найденной информации;
- если информации нет — честно говорить, что данных недостаточно.

Основные части системы:

1. Telegram layer
Отвечает за получение сообщений из Telegram и отправку ответов пользователю.

2. Backend API
Принимает webhook-запросы, управляет сервисами, логикой и зависимостями.

3. Knowledge base
Хранит очищенную и структурированную информацию о компании.

4. RAG pipeline
Ищет релевантные фрагменты базы знаний.

5. LLM service
Формирует финальный ответ через AI API.

6. Guardrails
Ограничивает галлюцинации и запрещает отвечать без контекста.

7. Evaluation
Проверяет качество retrieval и ответов.

Предпочтительная архитектура:

```text
app/
  api/
    telegram_webhook.py
  core/
    config.py
    logging.py
  services/
    telegram_service.py
    llm_service.py
    retriever.py
    rag_service.py
    guardrails.py
  schemas/
    telegram.py
    rag.py
  repositories/
    knowledge_repository.py
  prompts/
    assistant_prompt.py
  workers/
    ingestion.py
  main.py
```

Принцип:
API слой не должен содержать бизнес-логику.
Сервисный слой не должен напрямую зависеть от Telegram API, если это можно вынести.
RAG должен быть отдельным модулем.
LLM prompt должен быть отдельно от кода.

MCP-like context:
Если задача касается tools/resources, контрактов источников, metadata,
retrieval contracts или разделения LLM и данных, используй инструкции из
`prompts/codex/mcp/` как дополнительный источник проектных правил.
