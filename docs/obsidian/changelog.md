# FotoDesk AI — Changelog

Хронологическая запись всех изменений по сессиям.
Детали архитектуры → [04-architecture/](04-architecture/)
Воркфлоу → [05-workflows/](05-workflows/)

---

## [2026-04-04] — Monorepo + AI Backend + Тестирование

### Сделано
- Слияние двух проектов (`ai photo decltter` + `photodesk`) в единый monorepo
- Реструктуризация: `apps/frontend/`, `apps/backend/`, `core/ai/`, `infra/docker/`
- Перенос 7 HTML-страниц в `apps/frontend/` через `git mv` (история сохранена)
- Бэкенд Node.js/Express скопирован в `apps/backend/server.js` с исправлением 4 путей
- Добавлен Docker: `infra/docker/Dockerfile` + `docker-compose.yml` с named volumes
- GitHub Actions воркфлоу для деплоя `apps/frontend/` → GitHub Pages
- Firebase `firebase.json` обновлён: `public → apps/frontend`
- Добавлены: `README.md`, `.gitignore`, `.env.example`, `docs/system_memory.md`
- 5 страниц Notion: Product Overview, Architecture, Features, Current Status, Roadmap
- Obsidian документация: monorepo-structure, local-dev, deploy, prompt-system
- Скилл `/session-start` и `/session-end` для документирования сессий
- Добавлена ссылка "AI Cleaner" в сайдбар CRM с настройкой URL в Settings
- `RESULTS_DIR` прописан в `.env` → старые сессии видны в браузере (4 шт, 30 фото)

### Исправлено (баги в migration)
- `app.js`: неверный endpoint `/api/process` → `/api/process-image`
- `app.js`: `multer.single()` получал массив → последовательный цикл на каждый файл
- `app.js`: поле ответа `processedUrl` не существовало → `resultUrl` (XSS-safe DOM API)
- `server.js`: путь к `declutter.html` был `../photodesk/` → `../frontend/`
- `server.js`: краш при запросе без `multipart/form-data` → глобальный error handler
- `server.js`: `req.body` был `undefined` при non-multipart запросе → `(req.body || {})`
- `server.js`: `favicon.ico` возвращал 404 → добавлен маршрут `204 No Content`

### Известные проблемы / TODO
- `XAI_API_KEY` нужно прописать в `apps/backend/.env` для реальной обработки
- Aurora API: иногда возвращает разрешение ниже 2K (ограничение API, не промпта)
- GitHub Pages: при пуше напрямую в `main` обходит PR-правило — настроить branch protection
- Docker не тестировался в этой сессии (нет Docker на машине)

---

## [до 2026-04-04] — CRM + AI Declutter (pre-migration)

### Сделано
- CRM PhotoDesk: listings, orders, customers, calendar, packages, services, archive
- Firebase Firestore: 6 коллекций, правила безопасности
- AI Declutter: 9 типов комнат × 2 режима (declutter/empty)
- Aurora API интеграция с 7 форматами payload
- Автодетекция типа комнаты через Grok Vision
- Браузер сессий, сравнение до/после (4 режима: слайдер/до/после/рядом)
- Редактор промптов прямо в UI
- Python Grok Batch Cleaner (Tkinter desktop app)
- Полный аудит + 5 раундов исправлений (XSS, UX, баги)

---
