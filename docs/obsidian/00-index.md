# FotoDesk AI — Documentation Index

> Technical documentation for the FotoDesk AI monorepo.
> For high-level product docs, see Notion: FotoDesk AI workspace.

---

## Architecture

- [[04-architecture/monorepo-structure|Monorepo Structure]] — directory layout, what lives where

## Workflows

- [[05-workflows/local-dev|Local Development]] — running CRM, backend, Python app locally
- [[05-workflows/deploy|Deployment]] — Firebase Hosting, Railway, Docker

## AI Systems

- [[06-ai-systems/prompt-system|Prompt System]] — how prompts.json works, room types, modes

---

## Quick Reference

| Task | Command |
|------|---------|
| Start backend | `cd apps/backend && npm start` |
| Start with watch | `cd apps/backend && npm run dev` |
| Firebase deploy | `firebase deploy --only hosting` |
| Docker up | `docker-compose -f infra/docker/docker-compose.yml up -d` |
| Python batch app | `bash core/processing/grok_cleaner/run.sh` |
| Open AI UI | `http://localhost:3001/declutter` |
