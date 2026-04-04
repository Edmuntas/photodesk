# xAI Grok Vision API
*[[01-moc/PhotoDesk MOC|← MOC]]*

---

## Что это

xAI Grok Vision — мультимодальный AI от xAI (Илон Маск). Используется в Grok Batch Cleaner для редактирования и генерации изображений недвижимости.

---

## Задачи, которые решает API

| Задача | Режим | Описание |
|---|---|---|
| Удаление мебели | Image editing | Empty Room — чистые стены и пол |
| Очистка от беспорядка | Image editing | Declutter — организовать, не менять |
| Смена времени суток | Image editing | Day-to-Dusk — дневное → закатное |
| Смена неба | Image editing | 7 режимов освещения |
| HDR объединение | Image generation | Из 3-5 брекетинг снимков |
| Fallback генерация | Image generation | При ошибке editing endpoint |

---

## Технические детали

```
Провайдер:  xAI (x.ai)
API Base:   https://api.x.ai/v1
Endpoint:   /images/edits (primary)
            /images/generations (fallback)
Auth:       Bearer token (xai-...)
Config:     ~/.photodesk/grok_config.json → api_key
```

---

## Входные данные

```python
{
  "model": "grok-2-vision-latest",
  "prompt": "<системный промпт>",
  "image": "<base64 JPEG>",  # RAW конвертируется через rawpy
  "response_format": "b64_json"
}
```

**Ограничения:**
- Только JPEG перед отправкой (RAW конвертируется)
- Размер изображения — ограничения xAI API
- Rate limits — неизвестны точно, используется auto-retry

---

## Логика retry

```python
max_retries = 3
retry_on = [500, 503]          # Server errors → retry
fallback_on = [404, 405]       # Wrong endpoint → switch to /generations
```

---

## Промпт-система

Каждый тип комнаты × каждый режим = уникальный промпт.

Промпты редактируются в Таб 3 приложения и сохраняются в:
```
~/.photodesk/grok_config.json → prompts: { kitchen: "...", ... }
```

→ Подробнее: [[Prompts Library|Библиотека промптов]]

---

## Использование API-кредитов

⚠️ **Важно:** Каждый запрос к xAI тратит кредиты. Перед запуском большого батча убедиться в наличии кредитов.

Рекомендации:
- Тестировать на 2-3 фото перед большим батчем
- Не запускать автоматически без подтверждения пользователя
- Логировать успешные/неуспешные запросы
