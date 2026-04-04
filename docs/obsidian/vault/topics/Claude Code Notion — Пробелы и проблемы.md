---
created: 2026-04-02
type: topic
tags: [research, notebooklm, claude-code, notion, gaps, problems]
sources: [[Supercharging Notion with ClaudeCode]], [[I Deleted Notion and Heres My AI Workflow]], [[How to Automate Your Life and Work with Claude Code]]
notebook: "https://notebooklm.google.com/notebook/99f3728e-9c0d-4a31-b1f3-b0fe003afa52"
---

# Claude Code + Notion — Пробелы и нерешённые проблемы

На основе анализа источников, экосистема Claude Code + Notion имеет ряд существенных пробелов.

## 1. Ограничения интерфейса Notion

- **Сложные UI-элементы:** Claude не может работать с вложенными базами данных, toggle-блоками и linked databases через MCP [[Supercharging Notion with ClaudeCode]]
- **Ограниченный доступ к данным:** MCP видит только страницы с явно подключённой интеграцией — нет глобального поиска по всему workspace
- **Нет работы с медиа:** Claude не может загружать изображения, файлы и обрабатывать медиа-контент в Notion

## 2. Проблемы надёжности

- **Нестабильность API:** Notion API периодически возвращает ошибки, особенно при массовых операциях [[I Let Claude Code Build My Notion Automations]]
- **Rate limits:** При автоматизации больших баз данных быстро достигается лимит запросов
- **Потеря контекста:** Claude забывает предыдущий контекст между сессиями без явного CLAUDE.md [[How to Automate Your Life and Work with Claude Code]]

## 3. Отсутствующие workflows

- **Двусторонняя синхронизация:** Нет автоматической синхронизации изменений из Notion обратно в Claude
- **Real-time триггеры:** Claude не может реагировать на изменения в Notion в реальном времени (нужен n8n как посредник) [[Build ANYTHING with Claude Code and n8n]]
- **Мобильный доступ:** Нет удобного способа работать с Claude Code + Notion на мобильном устройстве
- **Шаблоны:** Отсутствуют стандартные шаблоны интеграции для типовых сценариев

## 4. Конкуренция и альтернативы

- Часть пользователей отказывается от Notion в пользу более AI-native инструментов [[I Deleted Notion and Heres My AI Workflow]]
- Obsidian + локальные Markdown-файлы часто предпочтительнее для ИИ-слоя [[How I Use Obsidian + Claude Code to Run My Life]]

## 5. Барьер входа

- Настройка MCP требует технических знаний (JSON-конфиги, API-токены) [[How to Connect Notion to Claude AI with Notion MCP]]
- Нет официального гайда от Anthropic для Notion-интеграции
- Документация разрозненная — каждый автор имеет свой подход

## Источники
- [[Supercharging Notion with ClaudeCode]]
- [[I Deleted Notion and Heres My AI Workflow]]
- [[How to Automate Your Life and Work with Claude Code]]
- [[Build ANYTHING with Claude Code and n8n]]
- [[How to Connect Notion to Claude AI with Notion MCP]]

---
*Сгенерировано: NotebookLM → Obsidian | 2026-04-02*
