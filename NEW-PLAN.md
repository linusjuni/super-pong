# Super Simple Beer Pong Tracker - Rebuild Plan

## Core Philosophy

**The system is a digital notebook that logs reality. It records what judges tell it. Nothing more.**

### Key Principles
1. **No game logic** - System doesn't know beer pong rules
2. **No validation** - Trust judges to enter correct data
3. **No calculations** - Frontend shows what's in the database
4. **Manual everything** - Judges control all state changes
5. **Statistics-first** - Data model optimized for querying player/team stats

## Why Rebuild?

Current app has accumulated complexity that fights the philosophy:
- Validation logic that rejects valid reality
- Auto-calculations that drift from ground truth
- Game rules enforcement that shouldn't exist
- Technical debt from "smart" features

Starting fresh allows building exactly what's needed: a simple, fast logging interface with powerful statistics.

---

## Data Model (5 Tables)

### 1. Player (persistent across all tournaments)
```python
- id: Integer (Primary Key)
- name: String (Unique) - "John Smith"
- created_at: DateTime
```

**Why:**
- Enables player statistics across all tournaments
- Prevents duplicate players from typos
- Easy to query "all shots by player X"

### 2. Tournament
```python
- id: Integer (Primary Key)
- name: String - "Summer 2024"
- created_at: DateTime
```

**Why:**
- Container for teams and games
- No status field needed (derive from games if needed)

### 3. Team (tournament-specific)
```python
- id: Integer (Primary Key)
- tournament_id: Integer (Foreign Key → Tournament)
- name: String - "The Champs"
- player1_id: Integer (Foreign Key → Player)
- player2_id: Integer (Foreign Key → Player)
```

**Why:**
- Same players can be on different teams in different tournaments
- Links to Player IDs for statistics
- No wins/losses fields (derive from games)

### 4. Game
```python
- id: Integer (Primary Key)
- tournament_id: Integer (Foreign Key → Tournament)
- team1_id: Integer (Foreign Key → Team)
- team2_id: Integer (Foreign Key → Team)
- winner_id: Integer (Foreign Key → Team, nullable) - Judges set manually
- status: String - "playing" or "finished"
- starting_cups_per_game: Integer - 6 or 10
```

**Why:**
- Ultra simple game tracking
- Winner is manually set by judges (no auto-detection)
- Status is manual (judges say when finished)

### 5. Shot (the event log)
```python
- id: Integer (Primary Key)
- game_id: Integer (Foreign Key → Game)
- player_id: Integer (Foreign Key → Player)
- team_id: Integer (Foreign Key → Team)
- timestamp: DateTime
- shot_type: String - "normal", "bounce", "trickshot"
- outcome: String - "miss", "hit", "rim"
- bounces: Integer (nullable) - Only for bounce shots
- elbow_violation: Boolean
```

**Why:**
- Simple event log of what happened
- Each shot is independent (no "turn" concept)
- Can be queried for any statistic
- Can be deleted (undo)
- No cup position tracking (adds complexity without value)

---

### API Endpoints (Pure CRUD)

#### Players
```python
GET    /api/players/              # List all players
GET    /api/players/search?name=  # Search by name (for autocomplete)
POST   /api/players/              # Create player
GET    /api/players/{id}          # Get player
GET    /api/players/{id}/stats    # Get player statistics
```

#### Tournaments
```python
GET    /api/tournaments/           # List all tournaments
POST   /api/tournaments/           # Create tournament
GET    /api/tournaments/{id}       # Get tournament
DELETE /api/tournaments/{id}       # Delete tournament
```

#### Teams
```python
POST   /api/tournaments/{id}/teams    # Add team to tournament
GET    /api/tournaments/{id}/teams    # List teams in tournament
PUT    /api/teams/{id}                # Update team
DELETE /api/teams/{id}                # Delete team
```

#### Games
```python
POST   /api/tournaments/{id}/games    # Create game
GET    /api/games/{id}                # Get game
PUT    /api/games/{id}                # Update game (set winner, status)
DELETE /api/games/{id}                # Delete game
```

#### Shots
```python
POST   /api/games/{id}/shots          # Log a shot
GET    /api/games/{id}/shots          # Get all shots for game
DELETE /api/shots/{id}                # Delete shot (undo)
```

#### Statistics
```python
GET    /api/tournaments/{id}/stats    # Tournament statistics
GET    /api/players/{id}/stats        # Player statistics
```

### No Services Layer

All endpoints are simple CRUD operations directly in routers:
- Create: `db.add(model); db.commit()`
- Read: `db.query(Model).filter(...).all()`
- Update: `model.field = value; db.commit()`
- Delete: `db.delete(model); db.commit()`

**No validation except:**
- Required fields are not null
- Foreign keys reference valid IDs

---

## Frontend Structure (React + Vite)

### File Structure
```
frontend/src/
├── main.jsx                    # Entry point
├── App.jsx                     # Router
├── services/
│   └── api.js                  # Axios client with all endpoints
├── components/
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   └── Modal.jsx
│   └── game/
│       ├── ShotLog.jsx         # List of shots with delete
│       └── ShotForm.jsx        # Form to log a shot
└── pages/
    ├── TournamentList.jsx      # Home - list all tournaments
    ├── TournamentSetup.jsx     # Create tournament & teams
    ├── GamesList.jsx           # List games in tournament
    ├── GamePlay.jsx            # Main game interface
    └── Statistics.jsx          # Statistics display
```

### Pages

#### 1. TournamentList.jsx (Home)
```
┌─────────────────────────────────────┐
│  Super Pong Tournaments  [New]      │
├─────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐    │
│  │ Summer 24  │  │ Fall 24    │    │
│  │ 8 teams    │  │ 6 teams    │    │
│  │ [View]     │  │ [View]     │    │
│  └────────────┘  └────────────┘    │
└─────────────────────────────────────┘
```

#### 2. TournamentSetup.jsx
```
┌─────────────────────────────────────┐
│  Create Tournament                   │
├─────────────────────────────────────┤
│  Name: [_____________]              │
│                                     │
│  Teams:                             │
│  ┌─────────────────────────────┐   │
│  │ Team Name: [__________]     │   │
│  │ Player 1:  [John▼] (search) │   │
│  │ Player 2:  [Sara▼] (search) │   │
│  │                        [X]   │   │
│  └─────────────────────────────┘   │
│  [+ Add Team]                       │
│                                     │
│  [Create Tournament]                │
└─────────────────────────────────────┘
```

**Player Selection:**
- Dropdown with search/autocomplete
- Shows existing players first
- Option to "Create new player: John Smith"
- Auto-creates player if name not found

#### 3. GamesList.jsx
```
┌─────────────────────────────────────┐
│  Summer 2024 Tournament             │
│  [Create Game] [Back]               │
├─────────────────────────────────────┤
│  Game 1: Team A vs Team B           │
│  Status: Playing │ Cups: 6 vs 4     │
│  [Continue]                          │
│                                     │
│  Game 2: Team C vs Team D           │
│  Status: Finished │ Winner: Team C  │
│  [View]                             │
└─────────────────────────────────────┘
```

**Create Game Modal:**
- Select Team 1 (dropdown)
- Select Team 2 (dropdown)
- Select starting cups per game (6 or 10)
- [Create]

#### 4. GamePlay.jsx (Main Interface)
```
┌─────────────────────────────────────────────────────────┐
│  Team A vs Team B                    [End Game] [Back]  │
├─────────────────────────────────────────────────────────┤
│  Log Shot:                                              │
│  Player: [John Smith ▼]                                │
│  Team:   [Team A ▼]                                     │
│  Type:   [Normal] [Bounce] [Trickshot]                 │
│  Result: [Miss] [Hit] [Rim]                            │
│  Bounces: [1] [2] [3] [4] [5] (if bounce)              │
│  [X] Elbow Violation                                    │
│  [Log Shot]                                             │
├─────────────────────────────────────────────────────────┤
│  Shot History:                                          │
│  • 10:45 PM - John (Team A) - Normal - Hit             │
│  • 10:44 PM - Sara (Team B) - Bounce (2x) - Hit  [Del] │
│  • 10:43 PM - Mike (Team A) - Normal - Miss     [Del]  │
└─────────────────────────────────────────────────────────┘
```

**Flow:**
1. Judges select shooting team and player
2. Select shot type and outcome
3. Click "Log Shot" - saves immediately
4. Shot appears in history
5. Can delete any shot (undo)
6. When game ends: click "End Game" → select winner → done

**Note:** No cup display. Physical table is source of truth.

#### 5. Statistics.jsx
```
┌─────────────────────────────────────┐
│  Summer 2024 - Statistics           │
├─────────────────────────────────────┤
│  Player Leaderboard:                │
│  1. John    65% (130/200 shots)    │
│  2. Sara    58% (87/150 shots)     │
│  3. Mike    52% (104/200 shots)    │
│                                     │
│  Team Standings:                    │
│  1. Team A     5-1                  │
│  2. Team B     4-2                  │
│  3. Team C     3-3                  │
└─────────────────────────────────────┘
```

---

## What Gets Eliminated

### ❌ No More
- Turn concept (just log shots individually)
- "Current team" logic
- Cup tracking/display (physical table is source of truth)
- Cup position tracking (no heatmaps)
- Automatic cup calculations
- Special events detection (balls back, two balls one cup)
- Shot validation (player on team, bounce rules, etc.)
- Game state management
- Complex game engine
- Auto winner detection
- Round-robin generation (judges create games manually)

### ✅ What Stays
- Digital log of every shot
- Player tracking across tournaments
- Manual game control
- Statistics queries
- Shot history with undo
- Simple, fast interface

---

## Statistics Capabilities

### Per Player (across all tournaments)
```sql
-- Hit percentage
SELECT
  COUNT(*) as total_shots,
  SUM(CASE WHEN outcome='hit' THEN 1 ELSE 0 END) as hits,
  AVG(CASE WHEN outcome='hit' THEN 1.0 ELSE 0 END) as hit_pct
FROM shots WHERE player_id = ?

-- Breakdown by shot type
SELECT
  shot_type,
  COUNT(*) as attempts,
  AVG(CASE WHEN outcome='hit' THEN 1.0 ELSE 0 END) as hit_pct
FROM shots
WHERE player_id = ?
GROUP BY shot_type

-- Elbow violations
SELECT COUNT(*) FROM shots
WHERE player_id = ? AND elbow_violation = true
```

### Per Tournament
```sql
-- Player leaderboard
SELECT
  players.name,
  COUNT(*) as shots,
  AVG(CASE WHEN outcome='hit' THEN 1.0 ELSE 0 END) as hit_pct
FROM shots
JOIN games ON shots.game_id = games.id
JOIN players ON shots.player_id = players.id
WHERE games.tournament_id = ?
GROUP BY players.id
ORDER BY hit_pct DESC

-- Team standings
SELECT
  teams.name,
  COUNT(CASE WHEN games.winner_id = teams.id THEN 1 END) as wins,
  COUNT(games.id) as games_played
FROM teams
LEFT JOIN games ON (games.team1_id = teams.id OR games.team2_id = teams.id)
WHERE teams.tournament_id = ?
GROUP BY teams.id
```

---

## Build Order

### Phase 1: Backend Foundation (2-3 hours)
1. Set up FastAPI project structure
2. Create 5 SQLAlchemy models (Player, Tournament, Team, Game, Shot)
3. Set up database connection
4. Create Pydantic schemas
5. Implement CRUD routers (one per model)
6. Test all endpoints with curl/Postman

**Key files:**
- `models/*.py` - 5 model files
- `schemas/*.py` - 5 schema files
- `routers/*.py` - 5 router files
- `main.py` - FastAPI app setup
- `database.py` - SQLAlchemy setup

### Phase 2: Frontend Foundation (2-3 hours)
1. Set up Vite + React project
2. Create API client with all endpoints
3. Create common components (Button, Card, Modal)
4. Create basic routing structure
5. Set up Tailwind CSS

**Key files:**
- `services/api.js` - All API endpoints
- `components/common/*.jsx` - Reusable UI
- `App.jsx` - Router setup

### Phase 3: Tournament Management (2-3 hours)
1. TournamentList page
2. TournamentSetup page with player autocomplete
3. GamesList page with manual game creation

**Features:**
- Create tournaments
- Add teams with player lookup
- Create games manually
- View all tournaments

### Phase 4: Game Play Interface (3-4 hours)
1. ShotForm component
2. ShotLog component (with delete)
3. GamePlay page integration
4. End game functionality

**Features:**
- Log shots individually
- View/delete shot history
- End game and select winner
- Clean, minimal interface

### Phase 5: Statistics (2-3 hours)
1. Statistics API endpoints
2. Statistics page with queries
3. Player profile pages
4. Tournament leaderboards

**Total estimated time: ~12-16 hours of focused work**

---

## Key Implementation Details

### Player Autocomplete
```javascript
// Frontend
const [playerSearch, setPlayerSearch] = useState('');
const [players, setPlayers] = useState([]);

useEffect(() => {
  if (playerSearch.length > 1) {
    api.get(`/players/search?name=${playerSearch}`)
      .then(res => setPlayers(res.data));
  }
}, [playerSearch]);

// Show existing players + "Create new: {name}" option
```

### Shot Logging
```javascript
// Simple POST on every shot
const shotData = {
  game_id: gameId,
  player_id: selectedPlayerId,
  team_id: selectedTeamId,
  shot_type: 'normal',
  outcome: 'hit',
  bounces: null,
  elbow_violation: false,
  timestamp: new Date()
};

await api.post(`/games/${gameId}/shots`, shotData);
```

### End Game
```javascript
// Manual winner selection
const handleEndGame = async (winnerTeamId) => {
  await api.put(`/games/${gameId}`, {
    status: 'finished',
    winner_id: winnerTeamId
  });
};
```

---

## Testing Strategy

### Manual Testing Checklist
- [ ] Create tournament with 4 teams
- [ ] Create 6 games manually
- [ ] Play game: log 20 shots
- [ ] Delete a shot (undo)
- [ ] End game and select winner
- [ ] View statistics
- [ ] Create another tournament with same players
- [ ] Verify player stats across tournaments

### Edge Cases to Verify
- Player with same name in different tournaments
- Deleting shots updates nothing else (no recalculation)
- Shot history shows most recent first
- Can create any matchup (no validation)
- Physical table is only cup reference needed

---

## Migration from Current App

### Option 1: Fresh Start (Recommended)
- Build new app from scratch
- Export old data as JSON
- Write import script if needed
- Deploy new app, retire old app

### Option 2: Data Export
If you have valuable historical data:

```sql
-- Export shots
SELECT
  players.name as player,
  games.id as game_id,
  shots.timestamp,
  shots.shot_type,
  shots.outcome
FROM shots
JOIN players ON shots.player_id = players.id
JOIN games ON shots.game_id = games.id

-- Import into new schema
```

---

## Deployment

### Simple Production Setup
```bash
# Backend
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Serve dist/ folder with any static file server
```

### Database
- SQLite file: `super_pong.db`
- Backup: Just copy the file
- No migrations needed (rebuild is fresh start)

---

## Success Criteria

✅ Judges can create tournament in < 2 minutes
✅ Judges can log shot in < 5 seconds
✅ Can undo any action (delete shot)
✅ Statistics show accurate player/team data
✅ No validation errors blocking valid actions
✅ System never "disagrees" with judges
✅ Interface is fast and distraction-free
✅ Physical table remains source of truth

---

## Philosophy Reminders

When building, always ask:
- "Does this trust the judges?"
- "Is the system just writing things down?"
- "Am I adding game logic? (Don't!)"
- "Can judges override this? (They should!)"

**The judges are always right. The system is always wrong.**

