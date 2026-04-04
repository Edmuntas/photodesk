---
created: 2026-04-02
type: topic
tags: [research, notebooklm, claude-code, notion, mcp]
sources: [[How to Setup Notion MCP in Claude Code]], [[Build your AI Second Brain with Notion and Claude MCP]], [[MCP + Notion The Ultimate PM Workflow]]
notebook: "https://notebooklm.google.com/notebook/99f3728e-9c0d-4a31-b1f3-b0fe003afa52"
---

# Автоматизация отчётности и управления проектами в Notion через MCP

Автоматизация отчётности и управления проектами в Notion через протокол MCP (Model Context Protocol) позволяет ИИ-ассистенту (Claude) напрямую взаимодействовать с рабочим пространством: читать данные, создавать страницы и изменять базы данных в реальном времени [[How to Setup Notion MCP in Claude Code]] [[How to Connect Notion to Claude AI with Notion MCP]].

## 1. Настройка подключения (Notion MCP)

- **Создание интеграции:** В настройках Notion создайте Internal Integration для получения API-ключа [[How to Setup Notion MCP in Claude Code]]
- **Предоставление доступа:** Добавьте интеграцию к конкретным страницам через меню «Connections» [[Build your AI Second Brain with Notion and Claude MCP]]
- **Конфигурация:** Токен добавляется в файл `mcp.json` для Claude Code

## 2. Автоматизация отчётности

- **Еженедельные отчёты:** Claude читает задачи из Notion, анализирует прогресс и создаёт сводку [[Claude Code + Notion = Weekly Status Report in 2 Min]]
- **Контент-планирование:** Генерация 30-дневного контент-календаря прямо в Notion [[Claude Code + Notion = 30 Day Content Calendar in 9 Minutes]]
- **Дашборды клиентов:** Автоматическое построение CRM-дашбордов [[Claude Just Built My Client Dashboard in Notion]]

## 3. Управление проектами

- **Kanban + Gantt:** Claude Code как project manager через MCP [[MCP + Notion The Ultimate PM Workflow]]
- **Обогащение данных:** ИИ автоматически заполняет свойства БД (приоритет, тип, ответственный) [[Unlock the 90% of Claude + Notion Power]]
- **Vibe Kanban:** Преобразование Claude Code в менеджер проектов [[Vibe Kanban + Claude Code]]

## 4. Рекомендуемая архитектура

- **Слой данных для ИИ:** Markdown-файлы со стратегией, SOP, голосом бренда → Claude Code читает при каждом запуске [[Supercharging Notion with ClaudeCode]]
- **Слой данных для людей:** Notion как визуальный интерфейс для CRM и задач → Claude записывает результаты через MCP
- **Гибридный подход:** Claude Code как «цифровой сотрудник» — работает в фоне, обновляет Notion [[I Built an AI Operating System with Claude Code AND Notion]]

## Источники
- [[How to Setup Notion MCP in Claude Code]]
- [[Build your AI Second Brain with Notion and Claude MCP]]
- [[MCP + Notion The Ultimate PM Workflow]]
- [[Claude Just Built My Client Dashboard in Notion]]
- [[Unlock the 90% of Claude + Notion Power]]

---
*Сгенерировано: NotebookLM → Obsidian | 2026-04-02*
