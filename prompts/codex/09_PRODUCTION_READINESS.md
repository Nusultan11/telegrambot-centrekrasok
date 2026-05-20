Ты работаешь над production readiness.

Цель:
Сделать проект ближе к реальному backend-сервису.

Проверяй:
- конфигурация через env;
- .env.example;
- Dockerfile;
- docker-compose.yml;
- structured logging;
- error handling;
- retries/timeouts;
- healthcheck endpoint;
- секреты не попадают в git;
- README содержит запуск;
- есть базовые тесты;
- зависимости зафиксированы;
- нет мусорных файлов;
- Telegram webhook можно настроить;
- AI API errors не роняют сервис.

Правила:
- не добавляй Kubernetes;
- не добавляй сложный monitoring stack;
- для MVP достаточно простого, чистого решения.

Формат ответа:

## Scope
Файлы.

## Production concern
Что улучшаем.

## Plan
План.

## Changes
Изменения.

## Operational result
Что теперь проще запускать/поддерживать.

## Remaining gaps
Что ещё не production-grade.

## Commit message
Пример:
chore: add dockerized application setup
