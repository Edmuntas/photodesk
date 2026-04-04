# Флоу обработки фото (Grok Cleaner)
*[[01-moc/PhotoDesk MOC|← MOC]]*

---

## Пайплайн обработки

```
ВХОДНЫЕ ДАННЫЕ
  └─► Папка с фото (JPG/RAW/DNG/...)

STEP 1: Подготовка
  ├─ JPEG/PNG/WebP → используются напрямую
  └─ RAW (DNG/CR2/NEF...) → rawpy конвертация → JPEG

STEP 2: Определение типа комнаты
  ├─ Авто: анализ имени файла
  │   kitchen/bedroom/living_room/bathroom/yard/hallway/balcony
  └─ Ручное: выбор из выпадающего списка

STEP 3: Выбор режима
  ├─ Режим обработки: Empty Room / Declutter / День→Закат
  └─ Освещение: Дневное / Золотой час / Закат / Сумерки / ...

STEP 4: Формирование промпта
  └─ Системный промпт (по типу комнаты) + режим + освещение

STEP 5: Отправка на xAI Grok Vision API
  ├─ POST /images/generations или /images/edits
  ├─ Payload: base64(image) + prompt + params
  └─ Auto-retry: 3 попытки при ошибках 500/503

STEP 6: Получение результата
  ├─ Success: сохранить в output/
  ├─ 404/405: Fallback → generate mode
  └─ Fail: лог ошибки, пропустить файл

ВЫХОДНЫЕ ДАННЫЕ
  └─► output/ папка — обработанные JPEG
```

---

## HDR Пайплайн (BETA)

```
ВХОДНЫЕ ДАННЫЕ
  └─► 3 или 5 снимков одной сцены (брекетинг)

STEP 1: Группировка
  ├─ Авто: по количеству (каждые 3 или 5 файлов = группа)
  └─ Ручная: drag файлы в группу

STEP 2: HDR промпт
  └─ Редактируемый HDR-промпт

STEP 3: Отправка
  └─ Группа → xAI API → один HDR результат

ВЫХОДНЫЕ ДАННЫЕ
  └─► filename_HDR.jpg
```

---

## Конфигурация API

```python
# xAI Grok Vision endpoint
API_BASE = "https://api.x.ai/v1"
ENDPOINT = "/images/edits"  # или /images/generations (fallback)

# Payload
{
  "model": "grok-2-vision-latest",  # предположительно
  "prompt": "<системный промпт> + <тип комнаты> + <освещение>",
  "image": "<base64 encoded JPEG>",
  "response_format": "b64_json"
}
```

---

## Точки боли

| Проблема | Влияние |
|---|---|
| Нет preview в приложении | Нужно открывать output папку вручную |
| Нет drag-and-drop | Неудобно выбирать файлы |
| HDR нестабильно | BETA статус — возможны артефакты |
| RAW конвертация медленная | DNG → JPEG добавляет время |
| Нет интеграции с CRM | Ручная загрузка результатов |
