---
name: session-end
description: Закрывает рабочую сессию — записывает что сделано в Obsidian changelog и обновляет Notion (Current Status + Roadmap). Запускается командой "/session-end", "закончи сессию", "запиши результаты", "обнови доку".
allowed-tools: [Read, Glob, Grep, Bash, Write, Edit, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-create-pages]
---

# Skill: session-end — Закрытие сессии и документирование

## Goal
Зафиксировать всё сделанное за сессию: обновить Obsidian changelog, обновить Notion (Current Status, Roadmap), чтобы следующая сессия начиналась с актуальной картиной.

## Input
Пользователь говорит: `/session-end`, `закончи сессию`, `запиши результаты`, `обнови доку`, `close session`, `задокументируй`.

## Steps

### Шаг 1 — Собери информацию о сессии

Выполни `git log --oneline -10` чтобы увидеть коммиты этой сессии.
Выполни `git diff HEAD~5 HEAD --stat` для общего объёма изменений.

Спроси пользователя (один вопрос, коротко):
> "Что ещё добавить в summary сессии? Новые баги, замечания, решения? (Enter — пропустить)"

Если пользователь молчит или говорит "нет" / "всё" — продолжай без его ввода.

### Шаг 2 — Обнови Obsidian changelog

Файл: `/Users/edmontmac16max/photodesk/docs/obsidian/changelog.md`

Если файл не существует — создай его с шапкой:
```markdown
# FotoDesk AI — Changelog

Хронологическая запись всех изменений по сессиям.
Детали архитектуры → [04-architecture/](04-architecture/)
Воркфлоу → [05-workflows/](05-workflows/)

---
```

Добавь новую запись В НАЧАЛО файла (после шапки) в формате:

```markdown
## [YYYY-MM-DD] — Название сессии (1-2 слова)

### Сделано
- [список конкретных изменений из git log + контекст]

### Исправлено
- [список багов, если были]

### Известные проблемы / TODO
- [если появились новые замечания]

---
```

### Шаг 3 — Обнови Notion: Current Status

Найди страницу: `mcp__claude_ai_Notion__notion-search` query="FotoDesk Current Status"
Затем `mcp__claude_ai_Notion__notion-fetch` — прочитай текущее содержимое.

Обнови страницу через `mcp__claude_ai_Notion__notion-update-page`:
- Добавь новые пункты в раздел "Что работает" (✅)
- Добавь/обнови пункты в "Баги fixed in migration" если чинили баги
- Обнови "Known Limitations" если появились новые
- Обнови дату вверху страницы

### Шаг 4 — Обнови Notion: Roadmap

Найди страницу: `mcp__claude_ai_Notion__notion-search` query="FotoDesk Roadmap"
Прочитай через `mcp__claude_ai_Notion__notion-fetch`.

Обнови через `mcp__claude_ai_Notion__notion-update-page`:
- Отметь выполненные пункты как `[x]` (было `[ ]`)
- Добавь новые пункты если пользователь упомянул новые идеи/задачи

### Шаг 5 — Обнови Notion: Architecture (если были структурные изменения)

Только если в сессии менялась структура файлов, API, схема БД — найди и обнови страницу "FotoDesk Architecture".

### Шаг 6 — Итоговое подтверждение

Выведи короткое резюме:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  СЕССИЯ ЗАКРЫТА  [дата]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Obsidian changelog  — обновлён
📋 Notion Current Status — обновлён
🗺️  Notion Roadmap       — обновлён

Коммиты этой сессии: N
Файлов изменено: N

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Notes
- Changelog пиши конкретно и кратко — не пересказывай весь код, только суть изменений
- Если Notion недоступен — запиши всё только в Obsidian и предупреди
- Не коммить changelog автоматически — пусть пользователь решает
- Дата берётся из системы (`date +%Y-%m-%d`)
