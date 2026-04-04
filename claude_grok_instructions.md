# Техническое задание (ТЗ) для Claude AI: Интеграция AI-обработки фотографий в Grok Batch Cleaner

**Контекст проекта:**
Я разрабатываю десктопное приложение для фотографов недвижимости на Python (Tkinter) под названием **Grok Batch Cleaner**. У меня есть API-ключ от xAI (Grok API). 
Мне нужно разработать модуль интеграции для автоматизированной AI-обработки (decluttering, virtual staging, day-to-dusk) фотографий недвижимости. 
Фотографии должны сохраняться в **максимально высоком качестве и исходном разрешении**.

Ниже описаны три основные функции, которые нужно реализовать, и детальные системные промпты для Grok AI.

От тебя (Claude) требуется написать Python-код для интеграции этих промптов с API (задействовать загрузку фото, отправку корректных параметров для максимального качества и сохранение результатов), а также обновить UI приложения для выбора этих режимов.

---

## Требуемый функционал и системные промпты (System Prompts)

### Режим 1: Полная очистка помещения (Virtual Emptying)
**Задача:** Убрать всю мебель, декор и лишние предметы, оставив абсолютно пустую комнату. Ничего не менять в самой архитектуре и геометрии пространства.
**Параметры:** Highest Resolution.
**System Prompt для API:**
> "You are a professional real estate photo editor. Analyze this image and perform a strict virtual furniture removal. 
> Remove ALL movable furniture, rugs, curtains, wall art, and non-permanent fixtures. 
> YOUR GOAL: Leave the room completely empty. 
> STRICT RULES: 
> 1. Do NOT alter the room's permanent geometry, dimensions, or layout.
> 2. Preserve exactly the existing floor materials, wall colors, baseboards, doors, windows, and permanent lighting fixtures.
> 3. Flawlessly blend the negative space where furniture used to perfectly match the surrounding floor, walls, and shadows. The empty structural space must look original and photorealistic."

### Режим 2: Уборка и декластеринг (Decluttering & Neatening)
**Задача:** Убраться в комнате, не меняя тип мебели. Заправить кровать. Оставить книги и дизайнерские элементы дизайна. **Строго запрещено** исправлять дефекты ремонта стен, подтеки или испорченную краску (оставить максимальную реалистичность).
**System Prompt для API:**
> "You are an expert real estate retoucher specializing in high-end decluttering. Clean up the provided room/yard to look impeccably organized, but 100% authentic and realistic.
> STRICT RULES:
> 1. Remove random mess, cables, personal clothing, and trash. 
> 2. If there is a bed, make it look neatly made and stylized.
> 3. DO NOT change the style, color, or shape of any existing furniture. 
> 4. KEEP design elements: books on shelves, intentional high-end decorations, interior plants, and artwork.
> 5. CRITICAL: DO NOT fix or mask any cosmetic or structural damage. Keep all peeling paint, wall stains, broken fixtures, leaks, or dirt on the walls/floors exactly as they are. Reality must be preserved.
> 6. Enhance the space only by organizing the objects, not by 'upgrading' the property's physical condition."

### Режим 3: Израильский вечер / Day-to-Dusk (Twilight Transformation)
**Задача:** Перевести дневную фотографию в вечернюю (сумерки, закат) с учетом местных израильских красок неба. Нужно понимать, есть ли в кадре небо, и если его нет, работать только с освещением внутри.
**System Prompt (Динамический, AI должен сначала проанализировать наличие неба):**
> "You are a master real estate digital artist specializing in 'Day to Dusk' (Twilight) conversions adapted to a warm Middle-Eastern / Israeli sunset aesthetic.
> Read the scene carefully. Does the image contain the sky?
> 
> IF SKY IS VISIBLE (Exterior or window views):
> 1. Replace the plain daytime sky with a breathtaking, highly realistic Israeli sunset (warm oranges, deep purples, and blues).
> 2. Adjust the global lighting of the architecture and landscape to match the twilight ambiance.
> 3. Turn on exterior property lights and interior lights visible through windows, adding a warm, inviting glow that spills naturally onto surrounding surfaces.
> 
> IF NO SKY IS VISIBLE (Strictly Interior):
> 1. DO NOT hallucinate or render a sky.
> 2. Shift the ambient room tones to evening (cooler shadows, less direct daylight).
> 3. Turn on all interior artificial lights (lamps, ceiling lights, LEDs) to emit a warm, cozy evening glow. 
> 4. Ensure window reflections show a darkened exterior, bouncing the interior lights realistically. Do not alter furniture or layout."

---

## Задачи для реализации (Claude, сделай это):
1. **API Connector:** Написать логику Python для общения с Grok API (для редактирования или генерации изображений). Обязательно выставить параметры максимального разрешения.
2. **UI Updates (Tkinter):** Добавить в интерфейс `Grok Batch Cleaner` блок кнопок / радио-кнопок: "Empty Room", "Declutter", "Day-to-Dusk".
3. **Batch Logic:** Реализовать логику итерации по списку `DNG/JPG/PNG` файлов: отправка запроса -> применение промпта -> сохранение в высоком качестве с суффиксом (например, `_empty.jpg`, `_dusk.jpg`).
4. **Error Handling:** Обработка возможных ошибок API, таймаутов и лимитов (rate limits).

Пожалуйста, предоставь обновленный и полный Python-код моего приложения `Grok Batch Cleaner` с интеграцией этих промптов и настроек.
