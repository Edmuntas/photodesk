---
name: session-start
description: Открывает брифинг перед рабочей сессией — читает Notion и Obsidian, показывает что сделано, что в плане, какие баги открыты. Запускается командой "/session-start", "начни сессию", "что у нас по плану", "что надо сделать".
allowed-tools: [Read, Glob, Grep, Bash, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Notion__notion-update-page]
---

# Skill: session-start — Брифинг перед сессией

## Goal
Прочитать состояние проекта из Notion и локального Obsidian, сформировать краткий брифинг: что сделано в прошлые сессии, что в планах, какие открытые баги/задачи.

## Input
Пользователь говорит: `/session-start`, `начни сессию`, `что у нас по плану`, `что надо сделать`, `брифинг`, `open session`.

## Steps

### Шаг 1 — Читаем Notion: страница "Current Status"

Используй `mcp__claude_ai_Notion__notion-search` с query="FotoDesk Current Status" чтобы найти страницу.
Затем `mcp__claude_ai_Notion__notion-fetch` — прочитай содержимое.

Из страницы извлечь:
- Раздел "Что работает" (✅)
- Раздел "Баги" или "Known issues" (⚠️ / 🔴)
- Раздел "Manual Step Required"

### Шаг 2 — Читаем Notion: страница "Roadmap"

`mcp__claude_ai_Notion__notion-search` query="FotoDesk Roadmap".
Затем `mcp__claude_ai_Notion__notion-fetch`.

Извлечь все незакрытые пункты ([ ]) из Short-term и Mid-term.

### Шаг 3 — Читаем локальный Obsidian changelog

Прочитай файл `/Users/edmontmac16max/photodesk/docs/obsidian/changelog.md` если существует.
Показать последние 3 записи.

### Шаг 4 — Читаем system_memory.md для контекста

`Read` файл `/Users/edmontmac16max/photodesk/docs/system_memory.md` — первые 60 строк.
Напомни ключевые ограничения AI (preserve defects, no adding elements, etc.)

### Шаг 5 — Формируем брифинг

Выводи в формате:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ФОТОДЕСК — БРИФИНГ СЕССИИ  [дата]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ПОСЛЕДНИЕ ИЗМЕНЕНИЯ (из changelog)
  • [список]

🐛 ОТКРЫТЫЕ БАГИ
  • [список из Notion Current Status]

📋 ПЛАН (из Notion Roadmap — Short-term)
  • [незакрытые пункты]

⚠️  ВАЖНЫЕ ОГРАНИЧЕНИЯ AI
  • [из system_memory.md]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Готов к работе. Что делаем сегодня?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Notes
- Если Notion недоступен — читай только локальные файлы и предупреди
- Не спрашивай пользователя лишних вопросов — выводи брифинг сразу
- После брифинга жди задачу от пользователя
