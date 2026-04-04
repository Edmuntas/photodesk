# FotoDesk AI — Changelog

Хронологическая запись всех изменений по сессиям.
Детали архитектуры → [04-architecture/](04-architecture/)
Воркфлоу → [05-workflows/](05-workflows/)

---

## [2026-04-04] — Исправление заказов + Система тестовых данных

### Сделано

**Исправление страницы Заказов (orders) — sync pipeline listings**
- Обнаружена проблема: `renderOrders()` брал данные из `store.orders` (кэш), а не из `store.listings` (источник истины) — новые нкасим в пайплайне не появлялись в заказах
- Исправлено: добавлен sync-блок в начало `renderOrders()` — для каждого нкаса в пайплайне вызывается `_ensureOrder(l)` + `_syncListingToOrder(l)` перед фильтрацией
- Исправлена краш ошибка `b.client.isExisting` при наличии старых бронирований в Firestore с другим форматом: добавлен `.filter(b => b.property && b.client)` + guard `b.package?.name`

**Система тестовых данных (`photodesk.html`)**
- Глобальный флаг `_testMode = false` — включается/выключается кнопкой в шапке списка нкасим
- Кнопка `🧪 מצב בדיקה` в строке управления: оранжевая когда активна, серая когда выключена
- При активном `_testMode` все новые нкасим / лекухот / агенты получают `isTest: true`
- Значок `🧪` (жёлтый бадж) отображается в: строках таблицы нкасим, карточках канбана, строках заказов в pipeline, карточках агентов (cards + rows)
- Кнопка `🗑 בדיקות` — появляется автоматически когда есть тестовые данные, прячется когда их нет
- `deleteTestData()` — hard delete (без архивации): удаляет из `store.listings`, `store.customers`, `store.orders` и из Firestore напрямую

### Исправлено
- `renderOrders()`: crash если в `filteredPending` есть элемент без `b.property` или `b.client` — добавлен guard фильтр

### Известные проблемы / TODO
- Бронирование B_AUDIT_001 в Firestore имеет устаревший формат (без поля `property`/`client`) — фильтруется и не показывается. Можно удалить из Firestore вручную если мешает
- При удалении тест-данных через диалог в Playwright — `confirm()` обрабатывается особым образом; в реальном браузере всё работает корректно

---

## [2026-04-04] — Аудит + Перевод AI Cleaner на иврит + Мобильный RTL

### Сделано

**Полный аудит проекта (Playwright + Firebase)**
- Сделаны скриншоты всех страниц: index, photodesk (login), booking, quote, declutter
- Проверен CRM — Firebase Auth, Firestore коллекции, Hebrew RTL — всё работает
- Созданы тестовые данные: лкоченты `שרה אברהם` (C_AUDIT_001) и `מוחמד חאלד` (C_AUDIT_002), нкасы `L_AUDIT_001` (הרצליה) и `L_AUDIT_002` (תל אביב)

**Исправление роутинга сервера (server.js)**
- Обнаружена проблема: только `/declutter` имел route, остальные страницы (photodesk, booking, quote и др.) возвращали 404
- Исправлено: добавлен `express.static(FRONTEND_DIR)` + явные routes для всех 6 страниц

**Перевод AI Cleaner (declutter.html) на иврит — полный**
- `lang="ru" dir="ltr"` → `lang="he" dir="rtl"`
- Заголовок: `עריכת תמונות`
- Topbar, табы, session bar, drop zone — на иврите
- Кнопки режимов: `ריקון` / `ניקוי` / `שמיים`
- Sky toolbar: `זמן:` / `עננים:` + 7 вариантов времени + 4 типа облаков
- Таблица очереди: все заголовки на иврите
- Room labels: все 11 типов комнат переведены
- Lighting moods: `יום` / `ערב` / `שעה כחולה` / `לילה`
- Viewer: `תצוגה מקדימה`, `לפני`/`אחרי`, сравнение, скачивание
- Модальные окна: Настройки и Редактор промптов — на иврите
- Все строки JS (log, confirm, статусы) — на иврите

**RTL CSS исправления**
- `border-right` → `border-left` (левая панель)
- `text-align:left` → `text-align:right` (заголовки таблицы)
- `margin-left` → `margin-right` (badges вариантов)
- `padding-right` → `padding-left` (список комнат в редакторе)
- `right:14px` → `left:14px` (кнопка закрытия модала)
- `justify-content:flex-end` → `flex-start` (кнопки сохранения)

**Мобильный адаптив (новый `@media` блок)**
- `≤768px`: layout меняется на колонку, левая панель — полная ширина, правая — `60vh`
- `≤480px`: скрывается колонка "תאורה" для экономии места, font size уменьшен

### Известные проблемы / TODO
- `XAI_API_KEY` должен быть прописан в `apps/backend/.env` для реальной обработки
- Sky mode и lighting mood не тестировались с реальным Aurora API — нужна проверка
- Landing page (`public/index.html`, Lumina) остался на английском — не ясно, используется ли

---

## [2026-04-04] — Per-photo освещение + Множественные варианты

### Сделано

**Per-photo lighting mood (apps/frontend/declutter.html)**
- Убран глобальный light-toolbar, заменён колонкой **"Свет"** в таблице очереди
- Каждая строка имеет свой `<select>`: ☀️ День / 🌇 Вечер / 💙 Синий час / 🌙 Ночь
- При смене режима (empty↔declutter↔sky) колонка Свет переключается на "—" для sky
- Модель файла расширена: `lightMood: 'day'`, `allResults: []`

**Множественные варианты одной фотографии**
- `f.allResults[]` аккумулирует все результаты обработки одного файла с метками (`☀️ День`, `🌇 Вечер` и т.д.)
- В статусной ячейке: значок **`×N`** при N>1 вариантах + кнопка **`🔁`** для добавления варианта
- Нажатие `🔁` сбрасывает статус в "wait" — меняешь Свет → Старт → новый результат добавляется к существующим, оригинал сохраняется
- **Variants strip**: под кнопками в viewer появляется ряд превьюшек всех вариантов, кликнув переключаешь "После" и кнопку скачивания

**Исправление структуры промптов освещения (server.js + prompts.json)**
- Обнаружена критическая проблема: qualityFooter rule (7) "Preserve all existing lighting" стоял ДО инструкции смены освещения и отменял её
- При активном `lightMood`: инструкция освещения теперь идёт **ПЕРВОЙ** в промпте как главная задача
- rule (7) заменяется на "lighting change is intentional" вместо противоречия
- Промпты переписаны: пронумерованные детальные инструкции для каждого режима (CEILING LIGHTS, LAMPS, WINDOWS, COLOR CAST, ATMOSPHERE)

### Известные проблемы / TODO
- Изменение освещения зависит от возможностей Aurora API — комнаты с окнами дают лучший результат
- Скилл session-end/session-start не перезагружается в текущей сессии — нужен перезапуск Claude Code
- Lighting transformation не тестировался с реальным API (нужна проверка)

---

## [2026-04-04] — Промпты + Небо + Переобработка + Скиллы

### Сделано

**Улучшение промптов (core/ai/prompts.json)**
- Добавлен `fixtureRule` — запрет перерисовки фикстур (раковина, плита, шкафы, унитаз, окна). Проблема: Aurora меняла стиль раковины при удалении предметов рядом
- Усилен `defectRule` — теперь явно запрещает добавлять новые трещины/пятна на стены (проблема: Aurora дорисовывала повреждения)
- `qualityFooter` дополнен пунктами (8) и (9): запрет менять фикстуры + вывод в максимальном разрешении
- Добавлен тип **детская** (empty + declutter): детская мебель, игрушки, наклейки на стенах
- Добавлен тип **сад** (empty + declutter): сад/двор с растениями, отдельно от парковки/фасада
- Кухонные промпты: новое явное предупреждение про заполнение стен без добавления повреждений

**Переобработка и удаление в viewer (apps/frontend/declutter.html)**
- Кнопка **🔄 Переобработать** — прогоняет то же оригинальное фото через Aurora заново, заменяет result в preview
- Кнопка **🗑 Удалить** — удаляет файл результата с сервера, сбрасывает статус в очереди
- Оба работают и из queue (свежая обработка), и из галереи сессий
- Новый endpoint `POST /api/reprocess` + `DELETE /api/sessions/:slug/image/:filename` в server.js

**Режим 🌅 Небо — замена неба и времени суток**
- Новый режим "🌅 Небо" в declutter UI (третья кнопка рядом с Опустошить / Уборка)
- Sky toolbar: 7 вариантов времени суток (Золотой час, Рассвет, Полдень, Пасмурно, Синий час, Драматично, Ночь)
- 4 варианта облаков + 🎲 Случайно + чекбокс "Одинаковые облака в сессии"
- Авто-определение сцены: дрон → aerial, двор/сад/балкон → outdoor, остальное → indoor
- Файлы `core/ai/skyPrompts.json` + `buildSkyPrompt()` в server.js
- Сессионная консистентность: один тип облаков фиксируется на всю сессию при первом фото
- Суффикс результата: `_sky_golden_1234567890.jpg`

**Исправление скиллов session-start / session-end**
- Скиллы теперь есть в `/Users/edmontmac16max/ai photo decltter/.claude/skills/`
- Причина проблемы: Claude Code искал скиллы относительно primary working directory, а они лежали в photodesk/

### Идеи для развития
- Пресеты неба по объектам: "стандартный пакет квартиры", "коттедж золотой час" — сохранить связку время+облака
- Batch-режим для неба: применить одно и то же небо ко всем outdoor-фотографиям сессии одним кликом
- Preview сравнения облаков: до запуска Aurora показывать рядом примеры вариантов неба (банк референсных фото)

### Известные проблемы / TODO
- Sky mode не тестировался с реальным Aurora API (теоретически корректен, нужна проверка)
- Skill tool возвращает "Unknown skill" внутри сессии — нужно перезапустить Claude Code

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
