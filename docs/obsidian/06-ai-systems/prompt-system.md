# Prompt System

## Overview

All AI prompts are stored in `core/ai/prompts.json`. The backend reads this file at runtime — changes take effect immediately without restarting the server (re-read on each request).

The web UI has a built-in prompt editor at `/declutter` (📝 button in the toolbar) that reads and writes this file via the `/api/prompts` endpoint.

## prompts.json Structure

```json
{
  "defectRule": "...",
  "qualityFooter": "...",
  "rooms": {
    "кухня": {
      "declutter": "...",
      "empty": "..."
    },
    "спальня": { ... },
    ...
  }
}
```

### Top-level keys

| Key | Purpose |
|-----|---------|
| `defectRule` | Appended to every prompt — explicitly forbids adding new defects AND forbids hiding existing ones |
| `qualityFooter` | Appended to every prompt — prohibits adding design elements, changing surfaces, altering perspective |
| `rooms` | Map of room type (Russian) → mode → prompt text |

### Room types

| Key | Room |
|-----|------|
| `кухня` | Kitchen |
| `спальня` | Bedroom |
| `гостиная` | Living room |
| `ванная` | Bathroom |
| `коридор` | Hallway/corridor |
| `балкон` | Balcony |
| `двор` | Yard/exterior |
| `дрон` | Drone/aerial shot |
| `по умолчанию` | Default (fallback for unknown room type) |

### Modes

| Mode key | Behaviour |
|----------|-----------|
| `declutter` | Remove personal clutter and items; keep furniture and room structure |
| `empty` | Remove everything movable; show bare shell ready for staging |

## How buildPrompt Works

In `apps/backend/server.js`:

```js
function buildPrompt(roomType, mode) {
  const prompts = JSON.parse(fs.readFileSync(PROMPTS_FILE, 'utf8'));
  const room = prompts.rooms[roomType] || prompts.rooms['по умолчанию'];
  const base = room[mode] || room['declutter'];
  return `${base}\n\n${prompts.defectRule}\n\n${prompts.qualityFooter}`;
}
```

Final prompt sent to aurora = `base` + `defectRule` + `qualityFooter`.

## Critical Rules (never remove from prompts)

These rules exist because prior prompt versions caused the AI to violate them:

1. **Preserve all defects** — wall stains, cracks, peeling paint, chipped tiles must remain visible. The AI was previously smoothing/hiding them.

2. **Do NOT add anything** — no new objects, design elements, cracks, or dirt. The AI was previously adding "realistic" wear to empty rooms.

3. **Do NOT change surfaces** — walls, floors, ceiling textures stay identical to original.

4. **REMOVE EVERY SINGLE ONE** — refrigerator magnets, notes, drawings, children's artwork must all be removed. Generic "remove clutter" was not sufficient.

5. **ALL towels without exception** — bathrooms: every towel must be completely removed, including those on floors or behind doors. The AI was previously leaving some.

## API Endpoints

```
GET  /api/prompts        → returns full prompts.json contents
PUT  /api/prompts        → overwrites prompts.json with request body
```

The PUT endpoint saves atomically (writes to temp file then renames). Invalid JSON is rejected with 400.

## Aurora API — 7 Format Attempts

The aurora image editing API has undocumented format requirements. `server.js` tries 7 different payload formats in sequence and uses the first successful response. This handles API version changes and format quirks without manual intervention.

## Room Detection

Before processing, the UI optionally calls:
```
POST /api/detect-room
Body: { image: <base64>, apiKey: "xai-..." }
```

Uses `grok-2-vision-1212` to analyze the image and return a room type string in Russian. The returned string is matched against the `rooms` keys in `prompts.json` (case-insensitive, trimmed). Falls back to `по умолчанию` if no match.
