# Frontend Philosophy

The frontend is a **judge's clipboard**. It presents forms and lists — the human decides what happened.

## Core Principles

- **No game logic.** The frontend does not enforce turn order, count remaining cups, or auto-detect winners. The judge inputs what they see, and the frontend sends it to the backend.
- **Radically simple.** Each page does one thing. Tournament list, tournament setup, games list, game play. No nested modals, no multi-step wizards.
- **Backend is the source of truth.** Every page fetches fresh data on mount. No client-side cache, no optimistic updates, no local state that drifts.

## Pages

- **TournamentList** — grid of tournament cards. Entry point.
- **TournamentSetup** — create a tournament, its teams, and auto-generate round-robin games in one submit.
- **GamesList** — all games for a tournament, grouped by team group (A/B). Add extra games manually.
- **GamePlay** — placeholder for now. Will be the shot-logging interface.

## Tech Stack

- **Vite + React** — fast dev server, zero-config builds.
- **shadcn/ui** — copy-pasted components, not a library dependency. Dark mode, New York style.
- **Tailwind CSS v4** — utility classes, no custom CSS.
- **Axios** — thin API client talking to the backend at `localhost:8000`.

## Running

```bash
cd frontend
npm install
npm run dev
```

Backend must be running on port 8000. See [BACKEND.md](./BACKEND.md).
