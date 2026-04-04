# Local Development

## Prerequisites

- Node.js 18+ (22 recommended)
- Python 3.10+
- Firebase CLI (`npm install -g firebase-tools`)
- xAI API key (from console.x.ai)

## 1. Environment Setup

```bash
cd /Users/edmontmac16max/photodesk
cp .env.example apps/backend/.env
# Edit apps/backend/.env:
#   XAI_API_KEY=xai-your-key-here
```

To use existing session history from before the migration:
```bash
# Add to apps/backend/.env:
RESULTS_DIR=/Users/edmontmac16max/ai photo decltter/results
```

## 2. CRM (PhotoDesk)

No backend needed. Open directly or use Firebase local server:

```bash
# Option A: Firebase local server (recommended — uses real Firestore)
firebase serve --only hosting
# Open http://localhost:5000/photodesk.html

# Option B: Open file directly
open apps/frontend/photodesk.html
```

## 3. AI Photo Declutter Backend

```bash
cd apps/backend
npm install
npm start          # production
npm run dev        # with --watch (auto-restart on file changes)
```

Open `http://localhost:3001/declutter`

### Verify the server is running

```bash
# Should return JSON array of sessions
curl http://localhost:3001/api/sessions

# Should return 200 HTML
curl -I http://localhost:3001/declutter

# Should return prompts JSON
curl http://localhost:3001/api/prompts | head -5
```

## 4. Python Batch Cleaner

```bash
# Easiest — script handles venv setup
bash core/processing/grok_cleaner/run.sh

# Manual
cd core/processing/grok_cleaner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 5. Running Tests

```bash
# Python cleaner tests
cd core/processing/grok_cleaner
python tests.py
```

## Common Issues

**`prompts.json` not found on server start**
- Verify `core/ai/prompts.json` exists: `ls core/ai/`
- Server resolves it relative to `apps/backend/server.js` — two directories up

**`declutter.html` returns 404 at `/declutter`**
- Server must be running — the file cannot be opened directly as `file://`
- Verify `apps/frontend/declutter.html` exists

**`ENOENT` on uploads or results directory**
- Server auto-creates these on first start via `fs.mkdirSync(..., { recursive: true })`
- If using custom `RESULTS_DIR`, verify the path exists and is writable
