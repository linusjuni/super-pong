# SuperPong 🏓🍺

Beer pong tournament tracker. Judges log shots, the system tracks stats.

**Players → Tournaments → Teams → Games → Shots.** Everything cascades down. No game logic enforced — the judge decides what happened.

## Run it

```bash
# Backend (FastAPI + SQLite)
cd backend && uv sync && uv run uvicorn app.main:app --reload

# Frontend (Vite + React)
cd frontend && npm install && npm run dev
```

API docs at [localhost:8000/docs](http://localhost:8000/docs). Frontend at [localhost:5173](http://localhost:5173).

## What's in the box

| Layer | Stack | Job |
|-------|-------|-----|
| **Backend** | FastAPI, SQLModel, SQLite | Pure CRUD + on-the-fly stats |
| **Frontend** | React, Vite, shadcn/ui, Tailwind | Judge's clipboard — forms & lists |
| **Stats** | SQL queries, TV-friendly slideshow | Auto-cycling dashboard for the big screen |
