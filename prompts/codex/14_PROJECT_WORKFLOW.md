# Как двигаться по проекту

## Большие шаги

| Шаг | Цель | Пример commit |
| --- | --- | --- |
| 1 | Инициализация backend-проекта | `chore: initialize backend project structure` |
| 2 | Telegram webhook | `feat: add telegram webhook handling` |
| 3 | Сбор и структура базы знаний | `feat: add company knowledge ingestion` |
| 4 | RAG retrieval | `feat: add company knowledge retrieval` |
| 5 | LLM generation | `feat: add grounded llm responses` |
| 6 | Guardrails | `feat: add hallucination guardrails` |
| 7 | Контекст диалога | `feat: add conversation context storage` |
| 8 | Evaluation | `test: add rag evaluation dataset` |
| 9 | Docker/README/production | `chore: add production-ready app setup` |

## Шаблон отчёта после каждого шага

```md
## Step completed
<Название шага>

## What was done
- ...

## What we achieved
- ...

## Files changed
- ...

## Architecture impact
Как это влияет на архитектуру проекта.

## RAG/LLM impact
Как это влияет на качество AI assistant.

## How to test
Команды или ручные проверки.

## Known limitations
Что пока не идеально.

## Next step
Что делаем дальше.

## Commit message
feat: ...
```

## Первый практический prompt

```md
## Big step
Initialize backend project structure

## Small step
Create clean FastAPI project skeleton for Telegram AI assistant

## Scope
Работай только с:
- app/
- pyproject.toml
- .env.example
- README.md
- .gitignore

## Ignore
Не открывай:
- data/
- notebooks/
- tests/
- logs/
- .venv/
- __pycache__/

## Focus
Создать минимальную чистую структуру backend-приложения без реализации RAG и LLM.

## Requirements
- FastAPI app entrypoint;
- config через pydantic-settings;
- базовая структура services/api/core/schemas;
- healthcheck endpoint;
- .env.example;
- понятный README skeleton.

## Constraints
- не добавлять Telegram logic;
- не добавлять RAG logic;
- не добавлять LLM calls;
- сначала план;
- потом изменения;
- после изменений отчёт и commit message.

## Expected result
Проект можно запустить локально, открыть healthcheck endpoint и увидеть базовую структуру будущего AI Telegram Assistant.

## Report format
### Scope
### Plan
### Changes
### Result
### How to test
### Risks
### Commit message
```

Первый commit:

```bash
git commit -m "chore: initialize backend project structure"
```
