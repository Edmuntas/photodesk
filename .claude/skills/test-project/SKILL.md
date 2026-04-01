---
name: test-project
description: Полное тестирование PhotoDesk — backend, frontend, UI, UX, accessibility. Запускается командой "протестируй весь проект" или "test".
allowed-tools: [Read, Glob, Grep, Bash, Agent, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_click, mcp__playwright__browser_evaluate, mcp__playwright__browser_console_messages, mcp__playwright__browser_wait_for, mcp__a11y__audit_webpage, mcp__a11y__get_summary, mcp__ux-expert__review_usability, mcp__ux-expert__analyze_accessibility, mcp__ux-expert__check_contrast, mcp__ux-expert__check_responsive, mcp__firebase__firebase_get_project, mcp__firebase__firestore_list_collections, mcp__firebase__firestore_query_collection, mcp__firebase__firebase_get_security_rules]
---

# Skill: test-project — Полное тестирование PhotoDesk

## Goal
Провести полный тест всего проекта: статический анализ кода, живое E2E тестирование через браузер, аудит доступности, UX-ревью и проверку Firebase backend. Вернуть единый структурированный отчёт с вердиктом PASS / FAIL.

## Input
Пользователь говорит: «протестируй весь проект», «test», «прогони тесты», «проверь систему».

## Scope

| Компонент | Инструмент | Что проверяем |
|-----------|-----------|---------------|
| Firebase backend | `mcp__firebase__*` | Коллекции, данные, правила безопасности |
| E2E браузер | `mcp__playwright__*` | Загрузка страниц, ключевые UI-флоу, JS-ошибки консоли |
| Accessibility | `mcp__a11y__*` | WCAG 2.1 AA нарушения, axe-core аудит |
| UX качество | `mcp__ux-expert__*` | Usability, контраст, responsiveness |
| Статический анализ | `Agent` (qa sub-agent) | JS ошибки, undefined functions, broken refs |

## Steps

### Шаг 1 — Firebase Backend (≈2 мин)

Используй `mcp__firebase__firebase_get_project` чтобы убедиться что проект `photodesk-45381` активен.

Используй `mcp__firebase__firestore_list_collections` для базы данных `(default)`:
- Ожидаемые коллекции: `customers`, `listings`, `orders`, `companies`, `bookings`, `store`
- Записать: какие есть, каких нет

Для каждой из этих коллекций `customers`, `listings`, `orders` — запусти `mcp__firebase__firestore_query_collection` (limit: 1) чтобы убедиться что данные есть и структура документа корректна.

Используй `mcp__firebase__firebase_get_security_rules` — проверить что правила не "allow all" (небезопасно).

**Критерии FAIL:**
- Проект недоступен
- Отсутствует коллекция `customers` или `listings`
- Security rules = `allow read, write: if true;` без условий

---

### Шаг 2 — E2E тест через Playwright (≈3 мин)

URL для тестирования: `https://edmuntas.github.io/photodesk/photodesk.html`
(Если нет интернета — использовать локальный файл: `file:///Users/edmontmac16max/photodesk/photodesk.html`)

**2.1 — Загрузка страницы**
```
mcp__playwright__browser_navigate → URL
mcp__playwright__browser_wait_for → selector: '#app' или 'body', timeout: 10000
mcp__playwright__browser_snapshot → записать структуру страницы
mcp__playwright__browser_console_messages → собрать все ошибки
```
Критерий: нет `[Error]` и `[Warning]` уровня критических в консоли.

**2.2 — Навигация по разделам**
Для каждого раздела кликнуть в боковом меню и проверить что контент отрисовался:
- לקוחות (клиенты) → ожидать `.customer-card` или `#customers-view`
- נכסים (объекты) → ожидать `.listing-card` или `#listings-view`
- הזמנות (заказы) → ожидать `#orders-view`
- חשבוניות (счета) → ожидать `#invoices-view`

```
mcp__playwright__browser_click → nav item selector
mcp__playwright__browser_wait_for → view selector, timeout: 3000
mcp__playwright__browser_snapshot → записать что видим
```

**2.3 — Открытие клиента**
Кликнуть на первую карточку клиента → ожидать открытия `#customer-panel.open` → сделать screenshot.

**2.4 — Проверка form inputs**
В панели клиента перейти на вкладку редактирования → убедиться что `#cp-company-select` содержит опции.

**2.5 — Кнопка мержа**
Убедиться что кнопка «🔀 מזג עם לקוח» присутствует → кликнуть → проверить что модальное окно `#merge-modal` открылось → закрыть.

Критерий FAIL: любой шаг timeout-ится или выбрасывает ошибку консоли.

---

### Шаг 3 — Accessibility Audit (≈1 мин)

```
mcp__a11y__audit_webpage → url: photodesk.html URL
mcp__a11y__get_summary → записать количество violations по severity
```

Дополнительно через ux-expert:
```
mcp__ux-expert__analyze_accessibility → контент страницы
mcp__ux-expert__check_contrast → для тёмной темы
mcp__ux-expert__check_responsive → mobile breakpoints
```

**Критерии FAIL:**
- Более 5 Critical violations axe-core
- Контраст ниже 4.5:1 для основного текста

---

### Шаг 4 — UX Review (≈1 мин)

```
mcp__ux-expert__review_usability → snapshot страницы клиентов
```

Проверить:
- Есть ли пустые состояния (empty states) когда нет данных
- Есть ли feedback на действия (toast-уведомления, индикаторы загрузки)
- RTL: весь текст и иконки выровнены справа

---

### Шаг 5 — Статический анализ (параллельно с шагами 2-4)

Запустить `Agent` с типом `qa` — он проверит код статически и вернёт отчёт.
Интегрировать его вердикт в финальный отчёт.

---

### Шаг 6 — Компиляция отчёта

Сохранить отчёт в `.tmp/qa_report_YYYY-MM-DD.md`.

## Output Format

```
# 🔍 PhotoDesk QA Report — [дата]
## Вердикт: PASS ✅ / FAIL ❌

---

## 🔥 КРИТИЧЕСКИЕ (блокируют работу)
- [компонент] Описание

## ⚠️ ВАЖНЫЕ (влияют на UX или данные)
- [компонент] Описание

## 💡 НЕЗНАЧИТЕЛЬНЫЕ (косметика, предупреждения)
- [компонент] Описание

---

## 📊 Детали по модулям

### Firebase Backend
- Проект: [статус]
- Коллекции: customers ✅ / listings ✅ / orders ✅ / ...
- Security rules: [OK / WARNING]

### E2E Playwright
- Загрузка страницы: ✅/❌
- Навигация разделов: ✅/❌ (X/4 прошли)
- Открытие клиента: ✅/❌
- Мерж-модал: ✅/❌
- JS ошибки в консоли: X ошибок

### Accessibility (axe-core)
- Critical violations: X
- Serious violations: X
- Контраст: ✅/❌

### UX Review
- RTL выравнивание: ✅/❌
- Empty states: ✅/❌
- Feedback на действия: ✅/❌

### Статический анализ
- Undefined functions: X
- Missing error handlers: X
- Broken refs: X

---

## Итог
X критических, Y важных, Z незначительных.
Полный отчёт: .tmp/qa_report_[дата].md
```

## Learnings
- Playwright требует что страница полностью загрузилась (Firebase init занимает ~2-3 сек) — всегда использовать `browser_wait_for` перед взаимодействием
- Локальные `file://` URL работают для базовой проверки HTML/CSS, но Firebase не инициализируется без сети
- a11y MCP лучше всего работает с живым URL на GitHub Pages, а не с локальным файлом
- security_reminder_hook блокирует Edit/Write с innerHTML — при исправлениях по результатам теста использовать только DOM-методы
