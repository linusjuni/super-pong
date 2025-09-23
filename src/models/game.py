from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import uuid
from .team import Team


class ShotType(Enum):
    NORMAL = "normal"
    BOUNCE = "bounce"
    TRICKSHOT = "trickshot"

class ShotOutcome(Enum):
    MISS = "miss"
    HIT = "hit"
    RIM = "rim"

class GameState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    PAUSED = "paused"


@dataclass
class Shot:
    """Individual shot record"""
    player_name: str
    team_name: str
    shot_type: ShotType
    outcome: ShotOutcome
    timestamp: datetime
    elbow_violation: bool = False
    cup_position: Optional[str] = None
    bounces: Optional[int] = None


class Game:
    def __init__(self, team1: Team, team2: Team, cups_per_team: int = 6):
        self.game_id = str(uuid.uuid4())
        self.team1 = team1
        self.team2 = team2
        self.cups_per_team = cups_per_team

        # Game state
        self.team1_cups_remaining = cups_per_team
        self.team2_cups_remaining = cups_per_team
        self.current_team = team1  # Team1 starts
        self.current_player = team1.player1  # Start with first player of team1
        self.state = GameState.NOT_STARTED
        self.winner: Optional[Team] = None

        # Game tracking
        self.shots: List[Shot] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.created_at = datetime.now()

        # Beer bong tracking
        self.team1_beer_bongs = 0
        self.team2_beer_bongs = 0

        # Additional notes
        self.game_notes: Optional[str] = None
