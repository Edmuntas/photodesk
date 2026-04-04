# Grok Batch Cleaner — Обзор
*[[01-moc/PhotoDesk MOC|← MOC]]*

---

## Что это

**Grok Batch Cleaner** — десктопное Python-приложение для пакетной AI-обработки фотографий недвижимости через xAI Grok Vision API. Работает локально на Mac/Windows.

---

## Для чего

| Задача | Что делает приложение |
|---|---|
| Убрать мебель | Режим "Пустая комната" — чистые стены и пол |
| Убрать беспорядок | Режим "Деклаттер" — порядок без изменения интерьера |
| Смена неба / освещения | 7 режимов (день, золотой час, закат, сумерки...) |
| HDR из брекетинга | Объединение 3-5 снимков в HDR |
| Пакетная обработка | Десятки фото за один прогон |
| RAW поддержка | DNG/CR2/CR3/NEF/ARW и другие форматы |

---

## Технический профиль

```
Язык:        Python 3
GUI:         Tkinter (стандартный)
AI API:      xAI Grok Vision (image editing endpoint)
RAW:         rawpy (конвертация перед отправкой)
Изображения: Pillow
Конфиг:      ~/.photodesk/grok_config.json
Запуск:      bash run.sh / python3 app.py
Размер:      app.py — 1,999 строк, tests.py — 689 строк
```

---

## Поддерживаемые форматы

```
JPEG, PNG, WebP, TIFF
DNG, CR2, CR3, NEF, ARW, RAF, RW2, ORF, PEF, SRW, X3F, RWL
```

---

## Связанные заметки
- [[Grok Cleaner Features|Все фичи Grok Cleaner]]
- [[06-ai-systems/Grok Vision API|Grok Vision API]]
- [[06-ai-systems/Prompts Library|Библиотека промптов]]
- [[05-workflows/Photo Processing Flow|Флоу обработки фото]]
