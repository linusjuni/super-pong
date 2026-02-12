# Backend Philosophy

The backend is a **digital notebook**. It logs what judges tell it — nothing more.

## Core Principles

- **No game logic.** The backend does not enforce rules, validate turns, count cups, or determine winners. The frontend (or human judge) decides what happened, and the backend records it.
- **No validation beyond data integrity.** Foreign keys must exist. That's it. If a judge says a shot was a hit, it's a hit.
- **Pure CRUD.** Every endpoint creates, reads, updates, or deletes a record. Stats are read-only queries computed at request time, never stored.
- **Undo = delete.** Logged a wrong shot? Delete it. No soft deletes, no reversal records.

## Data Model

Five entities, one direction of ownership:

```plaintext
Player (persists across tournaments)
  └─ Tournament
       ├─ Team (references 2 Players)
       │    └─ Game (references 2 Teams)
       │         └─ Shot (references 1 Player, 1 Team)
       └─ (cascade deletes flow downward)
```

- **Player**: just a name. Lives forever.
- **Tournament**: just a name. Owns teams and games.
- **Team**: name + 2 player references. Belongs to a tournament.
- **Game**: two teams + starting cup count. Has a status and optional winner. The frontend sets these when it decides the game is over.
- **Shot**: who threw, for which team, shot type, outcome, bounce count, elbow violation. Timestamped on creation.

## Tech Stack

- **SQLModel** — single class defines both the DB table and the Pydantic schema (no model duplication).
- **FastAPI** — async-capable, auto-generates OpenAPI docs at `/docs`.
- **SQLite** — zero-config, single-file database. Good enough for a beer pong tracker.

## Stats

Player and tournament stats are computed via raw SQL at query time. Nothing is cached or pre-aggregated. This keeps writes simple and means deleting/adding shots immediately reflects in stats.

## Running

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Database is created automatically on first startup. API docs at `http://localhost:8000/docs`.

Frontend expects this on port 8000. See [FRONTEND.md](./FRONTEND.md).
