# SuperPong 🏓🍺

Beer pong tournament tracker. Judges log shots, the system tracks stats.

**Players → Tournaments → Teams → Games → Shots.** Everything cascades down. No game logic enforced — the judge decides what happened.

## Run it

```bash
# Install all dependencies (from repo root)
uv sync --all-packages

# Backend (FastAPI + SQLite)
uv run --package super-pong-backend uvicorn app.main:app --reload

# Frontend (Vite + React)
cd frontend && npm install && npm run dev

# Elbow tracking
uv run --package elbow-tracking python elbow_tracking/elbow_tracking.py
```

API docs at [localhost:8000/docs](http://localhost:8000/docs). Frontend at [localhost:5173](http://localhost:5173).

## Dependencies

This is a uv workspace monorepo. Python dependencies are managed at the root with a single lockfile (`uv.lock`) and shared virtual environment (`.venv`).

Each Python project declares its own dependencies in its `pyproject.toml`:

- `backend/pyproject.toml` — FastAPI, SQLModel, etc.
- `elbow_tracking/pyproject.toml` — OpenCV, MediaPipe

To add a dependency to a specific project:

```bash
uv add --package super-pong-backend <package>
uv add --package elbow-tracking <package>
```

If both projects need it, add it to both. uv deduplicates in the lockfile — one resolved version, one install.

Frontend deps are managed separately with npm in `frontend/` (`npm install`, `npm run dev`).

## What's in the box

| Layer | Stack | Job |
| ----- | ----- | --- |
| **Backend** | FastAPI, SQLModel, SQLite | Pure CRUD + on-the-fly stats |
| **Frontend** | React, Vite, shadcn/ui, Tailwind | Judge's clipboard — forms & lists |
| **Elbow Tracking** | OpenCV, MediaPipe | Camera-based elbow violation detection |
| **Stats** | SQL queries, TV-friendly slideshow | Auto-cycling dashboard for the big screen |
