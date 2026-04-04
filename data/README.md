# Data Directory

This directory is **gitignored** — it contains only generated content that must not be committed.

## Session images
- Default path: `data/results/{session_name}/`
- Each session contains `*_original.jpg` and `*_empty_*.jpg` / `*_clean_*.jpg`
- Override path: set `RESULTS_DIR` in `.env`

## Temporary uploads
- Default path: `data/uploads/`
- Files are deleted automatically after processing
- Override path: set `UPLOADS_DIR` in `.env`

## Accessing previous sessions

Sessions processed before the monorepo migration live at:
```
~/ai photo decltter/results/
```

To make them accessible in the new server, add to `apps/backend/.env`:
```
RESULTS_DIR=/Users/edmontmac16max/ai photo decltter/results
```
