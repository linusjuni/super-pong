from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any

from pydantic import BeforeValidator
from sqlmodel import Field, Relationship, SQLModel


def _ensure_utc(v: Any) -> Any:
    """Attach UTC tzinfo to naive datetimes (e.g. loaded from SQLite)."""
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v


UTCDatetime = Annotated[datetime, BeforeValidator(_ensure_utc)]


# --- Enums ---


class ShotType(str, Enum):
    NORMAL = "normal"
    BOUNCE = "bounce"
    TRICKSHOT = "trickshot"
    RERACK = "rerack"


class ShotOutcome(str, Enum):
    MISS = "miss"
    HIT = "hit"
    RIM = "rim"
    NONE = "none"


class GameStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# Player
# ============================================================


class PlayerBase(SQLModel):
    name: str = Field(index=True, unique=True)


class Player(PlayerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: UTCDatetime = Field(default_factory=_utcnow)

    shots: list["Shot"] = Relationship(back_populates="player")
    punishment_bongs: list["PunishmentBong"] = Relationship(back_populates="player")
    teams_as_player1: list["Team"] = Relationship(
        back_populates="player1",
        sa_relationship_kwargs={"foreign_keys": "Team.player1_id"},
    )
    teams_as_player2: list["Team"] = Relationship(
        back_populates="player2",
        sa_relationship_kwargs={"foreign_keys": "Team.player2_id"},
    )


class PlayerCreate(PlayerBase):
    pass


class PlayerPublic(PlayerBase):
    id: int
    created_at: UTCDatetime


# ============================================================
# Tournament
# ============================================================


class TournamentBase(SQLModel):
    name: str


class Tournament(TournamentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: UTCDatetime = Field(default_factory=_utcnow)

    teams: list["Team"] = Relationship(
        back_populates="tournament",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    games: list["Game"] = Relationship(
        back_populates="tournament",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    punishment_bongs: list["PunishmentBong"] = Relationship(
        back_populates="tournament",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TournamentCreate(TournamentBase):
    pass


class TournamentPublic(TournamentBase):
    id: int
    created_at: UTCDatetime


# ============================================================
# Team
# ============================================================


class TeamBase(SQLModel):
    name: str
    player1_id: int = Field(foreign_key="player.id")
    player2_id: int = Field(foreign_key="player.id")
    group: str | None = None


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", index=True)

    tournament: Tournament = Relationship(back_populates="teams")
    player1: Player = Relationship(
        back_populates="teams_as_player1",
        sa_relationship_kwargs={"foreign_keys": "Team.player1_id"},
    )
    player2: Player = Relationship(
        back_populates="teams_as_player2",
        sa_relationship_kwargs={"foreign_keys": "Team.player2_id"},
    )
    games_as_team1: list["Game"] = Relationship(
        back_populates="team1",
        sa_relationship_kwargs={"foreign_keys": "Game.team1_id"},
    )
    games_as_team2: list["Game"] = Relationship(
        back_populates="team2",
        sa_relationship_kwargs={"foreign_keys": "Game.team2_id"},
    )


class TeamCreate(TeamBase):
    pass


class TeamUpdate(SQLModel):
    name: str | None = None
    player1_id: int | None = None
    player2_id: int | None = None
    group: str | None = None


class TeamPublic(TeamBase):
    id: int
    tournament_id: int


# ============================================================
# Game
# ============================================================


class GameBase(SQLModel):
    team1_id: int = Field(foreign_key="team.id")
    team2_id: int = Field(foreign_key="team.id")
    starting_cups_per_team: int = Field(default=6)


class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", index=True)
    winner_id: int | None = Field(default=None, foreign_key="team.id")
    status: GameStatus = Field(default=GameStatus.NOT_STARTED)
    started_at: UTCDatetime | None = Field(default=None)

    tournament: Tournament = Relationship(back_populates="games")
    team1: Team = Relationship(
        back_populates="games_as_team1",
        sa_relationship_kwargs={"foreign_keys": "Game.team1_id"},
    )
    team2: Team = Relationship(
        back_populates="games_as_team2",
        sa_relationship_kwargs={"foreign_keys": "Game.team2_id"},
    )
    winner: Team | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Game.winner_id"},
    )
    shots: list["Shot"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class GameCreate(SQLModel):
    team1_id: int
    team2_id: int
    starting_cups_per_team: int = 6


class GameUpdate(SQLModel):
    winner_id: int | None = None
    status: GameStatus | None = None
    started_at: UTCDatetime | None = None


class GamePublic(SQLModel):
    id: int
    tournament_id: int
    team1_id: int
    team2_id: int
    starting_cups_per_team: int
    winner_id: int | None
    status: GameStatus
    started_at: UTCDatetime | None


# ============================================================
# Shot
# ============================================================


class ShotBase(SQLModel):
    player_id: int = Field(foreign_key="player.id")
    team_id: int = Field(foreign_key="team.id")
    shot_type: ShotType
    outcome: ShotOutcome
    bounces: int | None = None
    elbow_violation: bool = False
    cup_position: int | None = None


class Shot(ShotBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id", index=True)
    timestamp: UTCDatetime = Field(default_factory=_utcnow)

    game: Game = Relationship(back_populates="shots")
    player: Player = Relationship(back_populates="shots")


class ShotCreate(SQLModel):
    player_id: int
    team_id: int
    shot_type: ShotType
    outcome: ShotOutcome
    bounces: int | None = None
    elbow_violation: bool = False
    cup_position: int | None = None


class ShotPublic(SQLModel):
    id: int
    game_id: int
    player_id: int
    team_id: int
    shot_type: ShotType
    outcome: ShotOutcome
    bounces: int | None
    elbow_violation: bool
    cup_position: int | None
    timestamp: UTCDatetime


# ============================================================
# Punishment Bong
# ============================================================


class PunishmentBongBase(SQLModel):
    player_id: int = Field(foreign_key="player.id")
    note: str | None = None


class PunishmentBong(PunishmentBongBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", index=True)
    timestamp: UTCDatetime = Field(default_factory=_utcnow)

    tournament: Tournament = Relationship(back_populates="punishment_bongs")
    player: Player = Relationship(back_populates="punishment_bongs")


class PunishmentBongCreate(SQLModel):
    player_id: int
    note: str | None = None


class PunishmentBongPublic(SQLModel):
    id: int
    tournament_id: int
    player_id: int
    note: str | None
    timestamp: UTCDatetime


# ============================================================
# Stats response models
# ============================================================


class PlayerStats(SQLModel):
    player_id: int
    player_name: str
    total_shots: int
    hits: int
    misses: int
    rims: int
    hit_percentage: float
    normal_hits: int
    normal_total: int
    bounce_hits: int
    bounce_total: int
    trickshot_hits: int
    trickshot_total: int
    elbow_violations: int


class PlayerLeaderboardEntry(SQLModel):
    player_id: int
    player_name: str
    total_shots: int
    hits: int
    hit_percentage: float


class TeamStanding(SQLModel):
    team_id: int
    team_name: str
    player1_name: str
    player2_name: str
    wins: int
    losses: int
    games_played: int


class TournamentStats(SQLModel):
    tournament_id: int
    tournament_name: str
    total_games: int
    completed_games: int
    player_leaderboard: list[PlayerLeaderboardEntry]
    team_standings: list[TeamStanding]


# Rebuild models for forward reference resolution
Player.model_rebuild()
Tournament.model_rebuild()
Team.model_rebuild()
Game.model_rebuild()
Shot.model_rebuild()
PunishmentBong.model_rebuild()
