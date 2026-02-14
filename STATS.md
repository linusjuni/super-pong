# Stats Dashboard

A full-screen, TV-friendly slideshow at `/tournaments/:id/stats`. Designed to run on a monitor during a tournament — no interaction needed.

## Philosophy

- **Passive viewing.** No buttons, no scrolling, no clicks. The dashboard auto-cycles through slides and re-fetches fresh data on every slide transition.
- **TV-first.** Large fonts, full viewport, dark background. Content must be readable from across the room.
- **One endpoint.** The backend serves everything in a single `GET /tournaments/{id}/dashboard` response. The frontend never makes multiple requests.

## Architecture

```plaintext
backend/app/stats.py                          ← All stat queries (pure functions, no HTTP)
backend/app/models.py                         ← DashboardStats response model

frontend/src/pages/StatsDashboard.jsx         ← Controller: fetch, auto-refresh, slide cycling
frontend/src/components/stats/SlideContainer.jsx        ← Full-screen wrapper + progress dots
frontend/src/components/stats/<SlideName>.jsx            ← One file per slide
```

## Adding a New Slide

Three steps:

### 1. Backend — add data to `DashboardStats`

Add any new fields to `DashboardStats` in `models.py`, and write the query in `stats.py`. Wire it into `get_dashboard()`. The frontend gets it for free on the next poll.

### 2. Frontend — create the slide component

Create `components/stats/YourSlide.jsx`. It receives the full `data` object as a prop:

```jsx
export default function YourSlide({ data }) {
  return (
    <div className="w-full max-w-6xl">
      {/* Your content */}
    </div>
  );
}
```

### 3. Frontend — register it in the slides array

In `StatsDashboard.jsx`, import your component and add it to the `slides` array:

```jsx
const slides = data
  ? [
      <TournamentStandingsSlide key="standings" data={data} />,
      <YourSlide key="your-slide" data={data} />,
    ]
  : [];
```

That's it. The cycling, transitions, and progress dots handle themselves.
