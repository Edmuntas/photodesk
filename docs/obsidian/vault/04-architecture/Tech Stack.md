# Стек технологий
*[[System Architecture|← Architecture]] | [[01-moc/PhotoDesk MOC|← MOC]]*

---

## Frontend (CRM)

| Компонент | Технология | Версия |
|---|---|---|
| Язык | HTML5 / CSS3 / Vanilla JS | ES6+ |
| CSS | Custom Properties + Flexbox/Grid | — |
| Шрифт | Heebo (Google Fonts) | — |
| Локализация | Иврит RTL (`direction:rtl`) | — |
| Firebase SDK | Firebase compat | v10.14.1 |
| PDF | Нативный browser print → PDF | — |

---

## Backend

| Компонент | Технология | Примечания |
|---|---|---|
| База данных | Cloud Firestore | NoSQL, real-time |
| Аутентификация | Firebase Auth | email/password |
| Хранилище файлов | Firebase Storage | Планируется |
| Хостинг CRM | GitHub Pages | Auto-deploy из main |
| Email | formsubmit.co | Для booking.html |

---

## Desktop App (Grok Cleaner)

| Компонент | Технология | Версия |
|---|---|---|
| Язык | Python 3 | 3.9+ |
| GUI | Tkinter | Стандартный |
| HTTP | requests | ≥2.31.0 |
| Изображения | Pillow | ≥10.0.0 |
| RAW конвертация | rawpy | ≥0.18.0 |
| SSL | certifi | ≥2024.2.2 |

---

## AI

| Компонент | Технология | Примечания |
|---|---|---|
| Image editing | xAI Grok Vision API | Batch processing |
| Промпты | Кастомные системные промпты | По типу комнаты |

---

## DevOps & Tooling

| Компонент | Технология |
|---|---|
| Версионирование | Git / GitHub |
| CI/CD | GitHub Pages (auto-deploy) |
| AI-ассистент | Claude Code (CLI) |
| Тестирование | Playwright (E2E), axe-core (a11y) |
| MCP серверы | Firebase, GitHub, Playwright, UX Expert, a11y |
| IDE | VS Code / Cursor / Windsurf |

---

## Firebase конфигурация

```javascript
const firebaseConfig = {
  projectId: "photodesk-45381",
  // + authDomain, storageBucket, appId, etc.
};
```

---

## Зависимости Grok Cleaner

```txt
requests>=2.31.0
Pillow>=10.0.0
rawpy>=0.18.0
certifi>=2024.2.2
```
