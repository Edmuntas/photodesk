# Системная архитектура PhotoDesk
*[[01-moc/PhotoDesk MOC|← MOC]]*

---

## Высокоуровневая схема

```
╔══════════════════════════════════════════════════════════╗
║                    PHOTODESK ECOSYSTEM                   ║
╠══════════════════╦═══════════════════════════════════════╣
║   PhotoDesk CRM  ║        Grok Batch Cleaner             ║
║   (Web App)      ║        (Desktop App)                  ║
╠══════════════════╩═══════════════════════════════════════╣
║                                                          ║
║  Клиент                                                  ║
║   └─► booking.html ──────────────────────────────────┐  ║
║        (4-step wizard)                                │  ║
║                                                       ▼  ║
║  Фотограф                                   Firebase     ║
║   └─► photodesk.html ◄──────────────── Firestore DB  ║
║        (CRM Dashboard)      │            └─ listings  ║
║             │               │            └─ customers ║
║             │               │            └─ companies ║
║             ▼               │            └─ orders    ║
║        quote.html           │            └─ bookings  ║
║        delivery.html        │            └─ store     ║
║        prepare.html         │                         ║
║                             │                         ║
║  Фотограф (локально)        │                         ║
║   └─► Grok Batch Cleaner    │                         ║
║        (Python/Tkinter)     │                         ║
║             │               │                         ║
║             ▼               │                         ║
║        xAI Grok Vision API  │                         ║
║        (image editing)      │                         ║
║             │               │                         ║
║             ▼               │                         ║
║        Processed Photos ────┘ (будущая интеграция)   ║
║                                                       ║
╚══════════════════════════════════════════════════════╝
```

---

## Модули системы

### 1. Web Frontend (photodesk.html)
```
Роль:        Single-page application
Тип:         Vanilla JS + Firebase SDK
Размер:      7,315 строк
Состояние:   Единый глобальный объект store{}
Навигация:   navigate(page) — виртуальная маршрутизация
```

**Архитектурные паттерны:**
- Глобальный `store` объект как state management
- Функции-рендереры для каждой страницы
- Firebase SDK для async операций
- localStorage как fallback кэш

### 2. Public Pages (клиентский фронтенд)
```
booking.html   — 4-step wizard (1,570 строк)
quote.html     — калькулятор стоимости (1,613 строк)
delivery.html  — галерея доставки (449 строк)
prepare.html   — гайд подготовки (752 строк)
```

### 3. Firebase Backend
```
Auth:      Firebase Authentication (email/password)
DB:        Cloud Firestore (NoSQL)
Storage:   Firebase Storage (планируется)
Hosting:   GitHub Pages (основное)
```

### 4. Desktop App (Grok Cleaner)
```
Язык:      Python 3
GUI:       Tkinter
API:       xAI Grok Vision
Конфиг:    ~/.photodesk/grok_config.json
```

### 5. AI Layer
```
Провайдер: xAI (Grok Vision)
Endpoint:  image editing / generation
Входные данные: JPEG (RAW конвертируется через rawpy)
Выход:     обработанные JPEG
```

---

## Поток данных (основной цикл)

```
1. ВХОД ЗАЯВКИ
   Client → booking.html → Firestore bookings/

2. ОБРАБОТКА ЗАЯВКИ
   Firestore bookings/ → photodesk.html Orders →
   Фотограф одобряет → Firestore listings/

3. ЦИТАТА
   photodesk.html → quote.html?id=LISTING_ID →
   Client подтверждает → listings/{id}.status = "מתוכנן"

4. СЪЁМКА И ОБРАБОТКА
   Гrok Cleaner (локально) → processed photos

5. ДОСТАВКА
   photos → Firebase Storage (план) → delivery.html →
   listings/{id}.deliveryStatus = "נמסר"

6. ОПЛАТА
   listings/{id}.paymentStatus tracked in CRM
```

---

## Связанные заметки
- [[Tech Stack|Стек технологий]]
- [[Firebase Structure|Структура Firebase]]
- [[Data Flow|Детальный поток данных]]
