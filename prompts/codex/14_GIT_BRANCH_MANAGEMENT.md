# 14_GIT_BRANCH_MANAGEMENT

Ты отвечаешь за чистое управление Git-ветками в проекте.

Цель:
Каждый большой шаг и каждый маленький подшаг должны выполняться в правильной отдельной ветке, без грязной истории, случайных файлов и смешанных изменений.

## Branch strategy

Основная ветка:
- main

Правило:
- main всегда должен оставаться стабильным;
- напрямую в main ничего не коммитить;
- каждый шаг делать в отдельной ветке;
- одна ветка = одна понятная задача;
- одна ветка не должна смешивать feature, refactoring, bug fix и docs.

## Branch naming

Используй понятные имена веток:

```bash
feature/backend-skeleton
feature/telegram-webhook
feature/knowledge-ingestion
feature/rag-retrieval
feature/llm-generation
feature/guardrails
feature/conversation-context
test/rag-evaluation
docs/readme
chore/docker-setup
fix/empty-retrieval-result
refactor/rag-service-boundaries
```

Запрещено использовать грязные названия:

```bash
new-branch
test
test2
v1
v2
final
final-fix
my-work
changes
update
```

## Step-to-branch rule

Перед началом каждого шага обязательно:

1. Проверить текущую ветку:

```bash
git branch --show-current
```

2. Проверить чистоту рабочей директории:

```bash
git status
```

3. Обновить main:

```bash
git checkout main
git pull origin main
```

4. Создать ветку под конкретный шаг:

```bash
git checkout -b feature/<step-name>
```

Пример:

```bash
git checkout -b feature/telegram-webhook
```

## Commit rules

Каждый маленький подшаг должен завершаться отдельным качественным commit.

Commit должен:

- описывать одно логическое изменение;
- быть понятным без просмотра diff;
- использовать Conventional Commits;
- не содержать временные слова: `v1`, `v2`, `final`, `fix2`.

Примеры хороших commit messages:

```bash
chore: initialize backend project structure
feat: add telegram webhook endpoint
feat: add company knowledge loader
feat: add retrieval service interface
feat: add grounded llm response generation
fix: handle empty retrieval results
refactor: separate rag orchestration from retriever
test: add rag evaluation cases
docs: document local setup
```

Плохие commit messages:

```bash
update
fix
final
changes
new version
bot works
v2
```

## Pull request rule

После завершения ветки:

1. Проверить статус:

```bash
git status
```

2. Запустить проверки:

```bash
ruff check .
pytest
```

3. Посмотреть diff:

```bash
git diff main...HEAD
```

4. Запушить ветку:

```bash
git push -u origin <branch-name>
```

5. Создать Pull Request в main.

PR должен содержать:

```md
## Summary
Что сделано.

## Scope
Какие файлы изменены.

## Why
Зачем это изменение нужно проекту.

## How to test
Как проверить.

## Risks
Что может сломаться.

## Commit
Главный commit message или список commits.
```

## Dirty branch prevention

Перед любым изменением проверяй:

```bash
git status
```

Если есть несвязанные изменения:

- не продолжай работу;
- не смешивай их с новой задачей;
- предложи один из вариантов:
  - commit текущих изменений;
  - stash текущих изменений;
  - отменить изменения;
  - создать отдельную ветку.

Команды:

```bash
git stash push -m "save unrelated changes"
git stash list
git stash pop
```

## Scope control

Ветка должна менять только файлы из текущего scope.

Если во время работы нужно изменить файл вне scope:

1. Остановись.
2. Объясни, зачем это нужно.
3. Предложи вынести это в отдельную ветку или отдельный шаг.

## Rebase / sync rule

Перед PR желательно подтянуть свежий main:

```bash
git checkout main
git pull origin main
git checkout <branch-name>
git rebase main
```

Если rebase вызывает конфликты:

- не скрывай это;
- покажи список конфликтующих файлов;
- исправь только конфликт;
- не добавляй новые изменения во время resolve.

## Report after each branch

После завершения ветки дай отчёт:

```md
## Branch completed
<branch-name>

## Step
<название шага>

## What was done
- ...

## Files changed
- ...

## Commits
- ...

## Git status
Чистая ли рабочая директория.

## How to test
Команды проверки.

## Pull request summary
Текст для PR.

## Next branch
Какую ветку создать следующей.
```

## Hard rules

Нельзя:

- коммитить напрямую в main;
- смешивать несколько задач в одной ветке;
- оставлять грязный `git status`;
- пушить `.env`, секреты, логи, кэш, `.venv`;
- делать ветки с названиями `v1`, `v2`, `final`;
- делать огромные commits без логической границы;
- делать refactor внутри feature-ветки без необходимости.

Нужно:

- одна ветка = один шаг;
- один commit = одно логическое изменение;
- чистый diff;
- понятный PR;
- стабильный main.

## Project branch map

| Большой шаг | Ветка | Commit |
| --- | --- | --- |
| Backend skeleton | `chore/backend-skeleton` | `chore: initialize backend project structure` |
| Telegram webhook | `feature/telegram-webhook` | `feat: add telegram webhook handling` |
| Knowledge ingestion | `feature/knowledge-ingestion` | `feat: add company knowledge ingestion` |
| RAG retrieval | `feature/rag-retrieval` | `feat: add company knowledge retrieval` |
| LLM generation | `feature/llm-generation` | `feat: add grounded llm responses` |
| Guardrails | `feature/guardrails` | `feat: add hallucination guardrails` |
| Evaluation | `test/rag-evaluation` | `test: add rag evaluation cases` |
| Docker setup | `chore/docker-setup` | `chore: add dockerized app setup` |
| README | `docs/readme` | `docs: add project README` |

GitHub flow обычно строится вокруг короткоживущих веток, commits, pull requests и merge в основную ветку после проверки. GitHub также описывает branch protection rules как способ защитить важные ветки от неподходящих изменений.

## Direct documentation links

```text
https://docs.github.com/en/get-started/using-git/about-git
https://docs.github.com/en/get-started/using-github/github-flow
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/about-branches
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
https://docs.github.com/en/pull-requests/collaborating-with-pull-requests
https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
https://git-scm.com/book/en/v2/Git-Branching-Rebasing
https://git-scm.com/docs/git-branch
https://git-scm.com/docs/git-switch
https://git-scm.com/docs/git-checkout
https://git-scm.com/docs/git-status
https://git-scm.com/docs/git-stash
https://git-scm.com/docs/git-rebase
https://www.conventionalcommits.org/en/v1.0.0/
```

Ключевая идея: ветка — это контейнер для одного шага. Если в одной ветке лежит Telegram webhook, refactor RAG, README и Docker — это грязная ветка. Правильно: разделить на 4 ветки и 4 понятных PR.
