# Deployment

## CRM — Firebase Hosting

```bash
# Deploy frontend only
firebase deploy --only hosting

# Dry run first (recommended)
firebase deploy --only hosting --dry-run
```

Firebase Hosting serves files from `apps/frontend/` (configured in `firebase.json`).

**firebase.json** public path:
```json
{
  "hosting": {
    "public": "apps/frontend"
  }
}
```

## CRM — GitHub Pages

GitHub Pages also serves from `apps/frontend/`.

**Required manual step after first push:**
GitHub → Settings → Pages → Source → `/apps/frontend` folder on branch `main`

After this, the site is live at: `https://edmuntas.github.io/photodesk/`

## Backend — Railway

1. Connect `Edmuntas/photodesk` repo in Railway dashboard
2. Set environment variable: `XAI_API_KEY=xai-...`
3. Start command: `node apps/backend/server.js`
4. Railway auto-detects Node.js and installs deps from `apps/backend/package.json`

> Note: Railway working directory is the repo root. `server.js` uses relative paths like `../../core/ai/prompts.json` which resolve correctly.

## Backend — Docker

```bash
# Build and start
docker-compose -f infra/docker/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker/docker-compose.yml logs -f

# Stop
docker-compose -f infra/docker/docker-compose.yml down
```

`XAI_API_KEY` must be set in your shell environment — docker-compose passes it through:
```bash
export XAI_API_KEY=xai-your-key-here
docker-compose -f infra/docker/docker-compose.yml up -d
```

Session data persists in Docker named volumes:
- `fotodesk_results` — processed session images
- `fotodesk_uploads` — temp uploads (auto-cleaned)

## Backend — Local (production mode)

```bash
cd apps/backend
NODE_ENV=production XAI_API_KEY=xai-... npm start
```

## Firestore Rules

```bash
# Deploy rules only
firebase deploy --only firestore:rules
```

## Full Deploy Sequence

```bash
# 1. Push code
git push origin main

# 2. Deploy Firebase Hosting + Firestore rules
firebase deploy

# 3. Start/restart backend (Railway auto-deploys on push)
# Or manually: ssh into server, git pull, restart process
```
