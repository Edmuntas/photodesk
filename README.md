# FotoDesk AI

Real estate photography toolkit — CRM, AI photo processing, and desktop batch cleaner in one monorepo.

## Products

| Product | Stack | Access |
|---------|-------|--------|
| **PhotoDesk CRM** | HTML/CSS/JS + Firebase Firestore | [edmuntas.github.io/photodesk](https://edmuntas.github.io/photodesk/photodesk.html) |
| **AI Photo Declutter** | Node.js + Express + xAI Grok API | `http://localhost:3001/declutter` |
| **Grok Batch Cleaner** | Python 3 + Tkinter + xAI API | `bash core/processing/grok_cleaner/run.sh` |

## Repository Structure

```
photodesk/
├── apps/
│   ├── frontend/          # All HTML pages (CRM + AI UI)
│   └── backend/           # Node.js/Express AI processing server
│       └── public/        # Legacy Lumina UI
├── core/
│   ├── ai/                # prompts.json, grok_models.json
│   └── processing/
│       └── grok_cleaner/  # Python desktop batch app
├── infra/
│   └── docker/            # Dockerfile + docker-compose.yml
├── data/                  # gitignored — generated sessions/uploads
├── docs/
│   ├── system_memory.md   # Full system reference
│   └── obsidian/          # Technical documentation vault
├── firebase.json
├── firestore.rules
└── .env.example
```

## Quick Start

### CRM (browser)
Open `https://edmuntas.github.io/photodesk/photodesk.html` or run Firebase Hosting locally:
```bash
firebase serve --only hosting
```

### AI Declutter backend
```bash
cp .env.example apps/backend/.env
# edit apps/backend/.env — set XAI_API_KEY
cd apps/backend && npm install
npm start
# Open http://localhost:3001/declutter
```

### Python desktop batch cleaner
```bash
cd core/processing/grok_cleaner
pip install -r requirements.txt
# or:
bash run.sh
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `XAI_API_KEY` | Yes | — | xAI Grok API key |
| `PORT` | No | `3001` | Backend server port |
| `RESULTS_DIR` | No | `data/results/` | Where processed sessions are saved |
| `UPLOADS_DIR` | No | `data/uploads/` | Temp upload directory |

## Deployment

### Firebase Hosting (CRM)
```bash
firebase deploy --only hosting
```

### Backend — Docker
```bash
docker-compose -f infra/docker/docker-compose.yml up -d
```
Set `XAI_API_KEY` in your shell environment before running.

### Backend — Railway
1. Connect this GitHub repo in Railway dashboard
2. Set `XAI_API_KEY` environment variable
3. Start command: `node apps/backend/server.js`

### Backend — local
```bash
cd apps/backend && npm start
```

## GitHub Pages

After pushing, update Pages source in GitHub:
**Settings → Pages → Source → `/apps/frontend` folder on branch `main`**

## Previous Sessions

Sessions processed before the monorepo migration are at `~/ai photo decltter/results/`.
To make them accessible in the new server, add to `apps/backend/.env`:
```
RESULTS_DIR=/Users/edmontmac16max/ai photo decltter/results
```
