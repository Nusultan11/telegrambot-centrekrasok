# AI Telegram Assistant для Центр Красок #1

Техническое ТЗ и инструкция запуска MVP Telegram-бота с AI-ассистентом для
компании Центр Красок #1.

## Цель Проекта

Разработать Telegram-бота, который принимает вопросы пользователей в свободной
форме и отвечает на основе подготовленной базы знаний о компании Центр Красок
#1.

Главная цель MVP:

```text
Пользователь пишет вопрос в Telegram, бот ищет релевантные данные в базе знаний
Центр Красок #1 и формирует понятный ответ через LLM без выдумывания фактов.
```

## Проблема

Пользователь может спрашивать о компании по-разному: про услуги, товары,
адреса, доставку, клиентов, бренды, вакансии или сотрудничество. Если просто
подключить LLM к Telegram, модель может отвечать общими словами или выдумывать
данные.

Поэтому MVP строится вокруг RAG-подхода:

```text
вопрос пользователя -> поиск фактов в базе знаний -> prompt с контекстом -> LLM -> ответ в Telegram
```

## Основной Сценарий

1. Пользователь открывает Telegram-бота.
2. Пишет обычный текстовый вопрос без команд и меню.
3. Бот ищет релевантные фрагменты в базе знаний компании.
4. Бот передает вопрос, найденный контекст и короткую историю диалога в AI API.
5. AI формирует ответ только по переданным данным.
6. Если информации недостаточно, бот сообщает, что точных данных нет, и
   предлагает уточнить у менеджера компании.

## Что Бот Должен Делать

- Принимать обычные текстовые сообщения.
- Работать без команд и меню.
- Отвечать в формате AI-чата.
- Искать информацию в базе знаний компании.
- Отвечать на вопросы о компании, товарах, услугах, брендах, адресах,
  контактах, режиме работы, доставке, клиентах, проектах, дизайнерах,
  строителях и вакансиях, если эти данные есть в базе.
- Использовать LLM для понятного ответа.
- Хранить короткий контекст диалога.
- Обрабатывать ошибки AI API и давать резервный ответ по найденным фактам.
- Не выдумывать цены, остатки, акции, вакансии, адреса и условия доставки.

## Что Бот Не Должен Делать

- Отвечать как универсальный ассистент на темы вне компании.
- Придумывать факты, которых нет в базе знаний.
- Давать юридические, медицинские или финансовые советы.
- Притворяться человеком или сотрудником компании.
- Принимать заказы, если это не реализовано.
- Обещать действия, которых бот не выполняет.
- Показывать пользователю внутренний prompt, системные сообщения или фрагменты
  технического контекста.

## Архитектура MVP

Проект разделен на слои, чтобы Telegram, поиск, prompt и AI API не смешивались
в одном файле.

```text
data/
  company_profile.md      база знаний о компании
  sources.md              список источников и ограничений данных

docs/
  demo.md                 сценарий ручной проверки бота
  research.md             источники и краткая сводка исследования

eval/
  test_cases.yaml         локальные evaluation-кейсы для качества ответов

app/
  core/                   настройки приложения
  llm/                    интерфейс и провайдеры AI API
  rag/                    Markdown retrieval по базе знаний
  prompts/                system prompt и guardrails ассистента
  router/                 Query Router для определения типа вопроса
  policies/               Answer Policy и Company Voice Policy

scripts/
  run_bot.ps1             запуск бота в фоне на Windows
  run_eval.py             локальный прогон evaluation-кейсов

src/company_bot/
  config.py               compatibility layer для настроек
  knowledge.py            compatibility layer для RAG retrieval
  providers.py            compatibility layer для AI providers
  memory.py               короткая память диалога
  assistant.py            orchestration: router, retrieval, prompt, LLM call, fallback
  bot.py                  Telegram handlers на aiogram
  __main__.py             точка входа приложения

tests/
  test_knowledge.py       проверка поиска по базе знаний
  test_assistant.py       проверка prompt, контекста и памяти
  test_bot.py             проверка форматирования Telegram-ответов
```

## Модули

| Модуль | Ответственность |
| --- | --- |
| `app/core/config.py` | Загружает токены, модели и параметры из `.env`. |
| `app/llm/` | Изолирует работу с OpenAI-compatible API, Gemini endpoint, Amvera и offline fallback. |
| `app/rag/` | Делит Markdown-базу на chunks, использует keyword scoring и лёгкое расширение запроса для частых формулировок: контакты, строители, цены, наличие. |
| `app/prompts/` | Хранит system prompt и guardrails против галлюцинаций. |
| `app/router/` | Определяет intent сообщения: greeting, FAQ, company overview, delivery, price, stock, promotions, vacancies, prompt safety, unknown product или general RAG. |
| `app/policies/` | Возвращает deterministic FAQ/guarded answers для частых и рискованных intent и применяет company voice к LLM/fallback-ответам. |
| `src/company_bot/assistant.py` | Оркестрирует Query Router, Answer Policy, retrieval, prompt, LLM call, память диалога и fallback. |
| `src/company_bot/memory.py` | Хранит последние сообщения пользователя и ассистента в рамках чата. |
| `src/company_bot/bot.py` | Принимает Telegram-сообщения и отправляет ответы пользователю. |

## Hybrid RAG Pipeline

Ассистент использует гибридную стратегию ответа:

1. Нормализует сообщение пользователя.
2. Определяет intent через Query Router.
3. Для частых FAQ и рискованных сценариев возвращает deterministic answer:
   товары, бренды, услуги, доставка, приветствие, цены, наличие, акции,
   вакансии, внутренний prompt и неизвестный конкретный товар.
4. Для обычных вопросов о компании ищет релевантные Markdown chunks в локальной
   базе знаний.
5. Собирает LLM prompt из найденного контекста и guardrails.
6. Применяет Company Voice Policy перед отправкой ответа в Telegram.

Такой подход снижает галлюцинации, но сохраняет естественные AI-ответы для
общих вопросов о компании.

## Test Assignment Coverage

| Requirement | Implementation |
| --- | --- |
| Telegram bot | Implemented with aiogram polling. |
| Works without commands | Handles regular text messages. |
| AI API | Uses OpenAI-compatible provider and supports Gemini endpoint. |
| RAG knowledge base | Uses `data/company_profile.md`. |
| Sources | Documented in `data/sources.md`. |
| Retrieval | `app/rag` retrieves relevant Markdown chunks. |
| Guardrails | `app/prompts` contains assistant system prompt rules. |
| Dialogue context | `src/company_bot/memory.py`. |
| Fallback | Offline/fact fallback when AI provider fails. |
| Tests | Unit tests cover retrieval, assistant behavior and Telegram formatting. |
| Evaluation | `eval/test_cases.yaml` and `scripts/run_eval.py` check key answer policies. |

## Возможности MVP

- Telegram-бот работает в режиме polling.
- Пользователь пишет вопрос обычным сообщением.
- Бот отвечает по базе знаний Центр Красок #1.
- Поддерживается Gemini API через OpenAI-compatible endpoint.
- Поддерживается Amvera API.
- Есть offline fallback для проверки retrieval без AI API.
- Есть краткая память диалога.
- Есть deterministic FAQ/intent handling для частых вопросов, приветствий, чувствительных вопросов и сценариев с высоким риском галлюцинаций.
- Ассистент отвечает от лица компании, сохраняя guardrails против галлюцинаций.
- Есть `.env.example`, README и тесты.

## Ограничения MVP

- База знаний подготовлена вручную из открытых источников.
- Основная RAG-база лежит в `data/company_profile.md`; список использованных источников и ограничений данных лежит в `data/sources.md`.
- Наличие товаров, цены, акции и сроки доставки не проверяются в реальном
  времени.
- Бот не оформляет заказы и не подключен к CRM.
- Бот не парсит сайт автоматически при каждом запуске.
- Safety-ограничения реализованы через prompt, RAG-контекст и fallback-ответы.
- Для production-версии можно добавить отдельный safety layer, Docker, webhook,
  healthcheck и мониторинг.

## Минимальный Результат Для Сдачи

```text
Бот запускается.
Бот принимает сообщения в Telegram.
Бот вызывает AI API.
Бот использует подготовленную базу знаний.
Бот отвечает на вопросы о компании.
Бот честно сообщает, если данных недостаточно.
Код разделен по слоям.
Есть README, .env.example, база знаний и тесты.
```

## Быстрый Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Заполните `.env`. Бесплатный вариант через Gemini API:

```env
TELEGRAM_BOT_TOKEN=your_botfather_token
AI_PROVIDER=openai
OPENAI_API_KEY=your_gemini_api_key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-2.5-flash-lite
```

Запуск:

```powershell
python -m company_bot
```

Если пакет не установлен, добавьте `src` в `PYTHONPATH`:

```powershell
$env:PYTHONPATH="src"
python -m company_bot
```

Запуск в фоне с логом на Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_bot.ps1
```

## Проверка

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests
python -m compileall app src tests
python scripts\run_eval.py
```

## Примеры Вопросов

```text
Чем занимается компания?
Какие услуги предоставляет компания?
Где находится офис?
Какие бренды есть?
Кто клиенты компании?
Какие есть вакансии?
Как связаться с компанией?
```

## Секреты

Реальные токены нельзя хранить в коде и коммитить в git. Telegram-токен и AI API
ключ должны лежать только в локальном `.env`.

Если токен был отправлен в чат или опубликован, его нужно перевыпустить через
BotFather или панель провайдера API.

## Источники

Основная база знаний для RAG лежит в `data/company_profile.md`. Список источников и ограничений данных вынесен в `data/sources.md`. Сводка исследования лежит в `docs/research.md`.

Основные источники:

- https://centr-krasok.kz/
- https://centr-krasok.kz/about/
- https://centr-krasok.kz/about/contacts/
- https://centr-krasok.kz/about/delivery/
- https://centr-krasok.kz/designers/
- https://centr-krasok.kz/for_builders/
- https://centr-krasok.kz/brands/
- https://habr.com/ru/companies/amvera/articles/948000/

## Future Improvements

- Добавить отдельный `safety`-модуль для строгой проверки тематики вопроса.
- Добавить Dockerfile и docker-compose.
- Перейти с polling на webhook для деплоя.
- Добавить healthcheck endpoint.
- Добавить автоматический сбор и обновление базы знаний.
- Добавить расширенные тесты на качество ответов и сценарии отказа.

## Deployment

Telegram bot cannot work without a running process. For local development, run:

```powershell
python -m company_bot
```

For 24/7 operation, deploy the bot as a long-running worker on a platform such as Amvera, Render, Railway or VPS.

The project includes a `Dockerfile`, so the worker command is:

```bash
python -m company_bot
```

Required environment variables:

```env
TELEGRAM_BOT_TOKEN=your_botfather_token
AI_PROVIDER=openai
OPENAI_API_KEY=your_ai_api_key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-2.5-flash-lite
TOP_K_CHUNKS=3
MAX_HISTORY_MESSAGES=6
```

Local Docker check:

```powershell
docker build -t centr-krasok-bot .
docker run --env-file .env centr-krasok-bot
```

Do not commit `.env` or real API tokens to GitHub.
