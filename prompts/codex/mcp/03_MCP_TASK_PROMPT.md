Ты работаешь над MCP-like частью проекта.

## Scope
Работай только с файлами, указанными в задаче.

## Required context
Перед изменениями прочитай релевантные файлы из:

- `prompts/codex/mcp/00_MCP_OVERVIEW.md`
- `prompts/codex/mcp/01_TOOL_CONTRACTS.md`
- `prompts/codex/mcp/02_RESOURCE_METADATA.md`

## Goal
Разделить AI-логику и источники данных так, чтобы retrieval, resources и
generation имели явные границы.

## Rules

- Tool/resource должен иметь понятный контракт.
- Retrieval не должен генерировать final answer.
- Generation не должен сам искать данные.
- Metadata обязательна для источников.
- Не добавляй сложную MCP-инфраструктуру, если для MVP достаточно локального
  контракта или интерфейса.
- Не смешивай MCP-like слой с Telegram handlers.

## Report format

### Scope
Файлы.

### MCP resource/tool
Что создаётся или улучшается.

### Plan
План.

### Changes
Изменения.

### Contract
Вход/выход.

### Hallucination control
Как это снижает риск выдуманных ответов.

### How to test
Как проверить.

### Commit message
Один Conventional Commit.
