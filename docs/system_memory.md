# FotoDesk AI — System Memory

> Last updated: 2026-04-04  
> Maintainer: Daron (Sisa Aero Photography) · edmontdoron@gmail.com

---

## What This System Does

Three products in one monorepo:

| Product | Stack | URL / Run |
|---------|-------|-----------|
| **PhotoDesk CRM** | HTML/CSS/JS + Firebase Firestore | `edmuntas.github.io/photodesk/photodesk.html` |
| **AI Photo Declutter** | Node.js + Express + xAI Grok API | `http://localhost:3001/declutter` |
| **Grok Batch Cleaner** | Python 3 + Tkinter + xAI API | `bash core/processing/grok_cleaner/run.sh` |

---

## AI Processing — Key Constraints

These rules are embedded in every prompt and **must never be violated**:

1. **Preserve all defects** — do NOT fix/hide wall stains, cracks, peeling paint, chipped tiles. Never invent new damage either.
2. **Do NOT add anything** — no new objects, no design elements, no cracks, no dirt, no grunge
3. **Do NOT change surfaces** — walls, floors, ceiling textures stay exactly as in original
4. **Do NOT redesign** — this is photo editing, not interior design

### Items that MUST always be removed:
- Refrigerator: ALL magnets, notes, drawings, stickers, photos, calendars
- Bathrooms: ALL towels (hanging, folded, on floor — every single one)
- Bathrooms: ALL toiletries (every bottle, tube, container)
- All rooms: personal family photos and frames

---

## Processing Modes

| Mode | Key (`mode` param) | Behaviour |
|------|--------------------|-----------|
| Empty shell | `empty` | Remove everything movable, show bare room |
| Clean & stage | `declutter` | Remove clutter/personal items, keep furniture |

---

## AI Processing Pipeline

```
1. User uploads image(s) via declutter.html UI
2. UI optionally calls POST /api/detect-room (Grok Vision → room type in Russian)
3. UI calls POST /api/process-image with {mode, roomType, sessionFolder, image}
4. server.js: buildPrompt(roomType, mode) → base + defectRule + qualityFooter
5. server.js: tries 7 API payload formats to POST https://api.x.ai/v1/images/edits
6. On success: saves original + processed to data/results/{sessionSlug}/
7. Returns {success, resultUrl, originalUrl, sessionFolder}
```

### Room types (Russian, used as keys):
`кухня` · `спальня` · `гостиная` · `ванная` · `коридор` · `балкон` · `двор` · `дрон` · `по умолчанию`

### AI Model used:
- Image editing: `aurora` (default) — accepts base64 or URL, returns processed image
- Room detection: `grok-2-vision-1212` — returns room type string

---

## Firebase Collections (CRM)

| Collection | Purpose | Access |
|------------|---------|--------|
| `listings` | Property jobs (нкасим) | Owner only |
| `customers` | Client contacts | Owner only |
| `companies` | Real estate agencies | Owner only |
| `bookings` | Public booking orders | Create: public; R/U/D: owner |
| `store/data` | Packages, services, schedule | Read: public; Write: owner |
| `archive` | Soft-deleted records | Owner only |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `XAI_API_KEY` | Yes | — | xAI Grok API key (stored client-side in localStorage `pd_api_key`) |
| `PORT` | No | `3001` | Backend server port |
| `RESULTS_DIR` | No | `data/results/` | Where processed sessions are saved |
| `UPLOADS_DIR` | No | `data/uploads/` | Temp upload directory |

---

## Known Limitations

- Aurora model output resolution may be lower than 2K (API limitation, not prompt-controllable)
- No batch API endpoint — images processed sequentially, one per request
- API key stored in browser localStorage (acceptable for single-user internal tool)
- `declutter.html` must be served by Node.js backend (not openable as bare file)

---

## Deployment

| Service | How |
|---------|-----|
| CRM (Firebase Hosting) | `firebase deploy --only hosting` |
| CRM (GitHub Pages) | Auto on push to `main` (source: `apps/frontend/`) |
| Backend (local) | `cd apps/backend && npm start` |
| Backend (Docker) | `docker-compose -f infra/docker/docker-compose.yml up` |
| Backend (Railway) | Connect GitHub repo, set `XAI_API_KEY`, start: `node apps/backend/server.js` |
| Python desktop app | `bash core/processing/grok_cleaner/run.sh` |
