# Библиотека промптов — Grok Vision
*[[Grok Vision API|← Grok API]] | [[01-moc/PhotoDesk MOC|← MOC]]*

---

## Базовые режимы (системные промпты)

### 1. Empty Room (Пустая комната)
```
You are a professional real estate photo editor.
Your task: completely remove ALL furniture, personal belongings,
decorations, and movable objects from the room.
Keep: walls, floors, ceilings, windows, built-in fixtures (kitchen cabinets,
built-in wardrobes), architectural elements.
Result must look like a perfectly clean empty room ready for staging.
Do not add any new furniture or objects.
Maintain realistic lighting and shadows.
```

---

### 2. Declutter (Деклаттер)
```
You are a professional real estate photo editor.
Your task: declutter and organize the room.
Remove: clutter, personal items, dirty dishes, papers, toys, trash.
Keep: furniture, decor items in place, the authentic feel of the space.
DO NOT: fix physical damage, cracks, stains on walls.
DO NOT: add or remove furniture.
Result should look like a tidy, lived-in home ready for photography.
```

---

### 3. Day-to-Dusk (День → Сумерки)
```
You are a professional real estate photo editor specializing in twilight conversions.
Convert this daytime exterior/interior photo to an Israeli golden sunset scene.
Sky: warm orange-pink-purple sunset sky, realistic for Mediterranean Israel.
Windows: add warm interior lighting visible through windows.
Exterior: warm golden-hour lighting on the building facade.
Do not change the architecture or structure.
Result should look like a professional twilight real estate photo.
```

---

## Режимы освещения (модификаторы к базовым промптам)

| Режим | Модификатор промпта |
|---|---|
| ☀️ Дневное небо | `Replace sky with bright blue summer sky, natural daylight` |
| 🌅 Золотой час | `Replace sky with golden hour, warm yellow-orange tones, 1 hour before sunset` |
| 🌄 Закат | `Israeli Mediterranean sunset, orange-pink-purple sky, dramatic and warm` |
| 🌆 Сумерки | `Blue hour twilight sky, deep blue purple, city lights beginning to appear` |
| 💡 Яркий интерьер | `Enhance interior lighting to bright and airy, soft shadows, professional photography look` |
| 🕯️ Вечерний | `Warm cozy evening interior lighting, soft warm tones, inviting atmosphere` |

---

## Промпты по типу комнаты

| Комната | Авто-определение по файлу | Специфика |
|---|---|---|
| kitchen | kitchen, מטבח | Акцент на столешницы, шкафы |
| bedroom | bedroom, חדר שינה | Акцент на кровать, гардероб |
| living_room | living, salon, סלון | Акцент на диван, TV-зона |
| bathroom | bathroom, שירותים | Акцент на плитку, сантехнику |
| yard | yard, garden, חצר | Акцент на зелень, патио |
| hallway | hallway, מסדרון | Акцент на входную зону |
| balcony | balcony, מרפסת | Акцент на вид, перила |

---

## Хранение и редактирование

Промпты хранятся в `~/.photodesk/grok_config.json` и редактируются прямо в приложении (Таб 3 "Prompts"). Изменения немедленно применяются к следующему батчу.
