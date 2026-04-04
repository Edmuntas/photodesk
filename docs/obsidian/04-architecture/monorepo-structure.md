# Monorepo Structure

## Directory Layout

```
photodesk/                          ← git root (Edmuntas/photodesk)
├── apps/
│   ├── frontend/                   ← HTML pages served by Firebase + GitHub Pages
│   │   ├── photodesk.html          ← CRM main app
│   │   ├── declutter.html          ← AI Photo Declutter UI (requires Node.js backend)
│   │   ├── booking.html
│   │   ├── quote.html
│   │   ├── prepare.html
│   │   ├── delivery.html
│   │   ├── import.html
│   │   └── index.html
│   └── backend/                    ← Node.js/Express AI processing server
│       ├── server.js
│       ├── package.json
│       └── public/                 ← Legacy Lumina UI (standalone, optional)
│           ├── index.html
│           ├── css/styles.css
│           └── js/app.js
├── core/
│   ├── ai/
│   │   ├── prompts.json            ← All room-type × mode prompt templates
│   │   └── grok_models.json        ← Model IDs and API config
│   └── processing/
│       └── grok_cleaner/           ← Python 3 Tkinter desktop batch app
│           ├── app.py
│           ├── tests.py
│           ├── requirements.txt
│           └── run.sh
├── infra/
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml
├── data/                           ← gitignored — generated content only
│   ├── .gitkeep
│   └── README.md                   ← explains session storage and legacy path
├── docs/
│   ├── system_memory.md            ← full system reference (AI context file)
│   └── obsidian/                   ← this vault
│       ├── 00-index.md
│       ├── 04-architecture/
│       ├── 05-workflows/
│       └── 06-ai-systems/
├── firebase.json                   ← Firebase CLI config (must stay at root)
├── firestore.rules
├── .firebaserc
├── .gitignore
├── .env.example
└── README.md
```

## Key Design Decisions

### Firebase files at root
Firebase CLI requires `firebase.json`, `firestore.rules`, and `.firebaserc` to be in the repository root. Do not move them.

### HTML in apps/frontend
Moved from root to `apps/frontend/` so Firebase Hosting and GitHub Pages both serve from the same source directory. Both point to `apps/frontend/`.

### Backend completely separate from frontend
`server.js` serves `declutter.html` via `/declutter` route, but the HTML file itself lives in `apps/frontend/`. The path in `server.js`:
```js
path.join(__dirname, '..', 'frontend', 'declutter.html')
```

### data/ is fully gitignored
Processed sessions (results/) and temp uploads (uploads/) are never committed. The `data/.gitkeep` file ensures the directory exists in the repo. The `RESULTS_DIR` env var can point to the old location to preserve access to pre-migration sessions.

### prompts.json in core/ai
Shared by both the Node.js backend (`apps/backend/server.js`) and potentially the Python batch cleaner. Path resolved at runtime:
```js
path.join(__dirname, '..', '..', 'core', 'ai', 'prompts.json')
```
