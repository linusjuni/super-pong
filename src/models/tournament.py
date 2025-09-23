# models/tournament.py
from typing import List, Optional
import uuid
from datetime import datetime

from .team import Team
from .game import Game


class Tournament:
    """Manages a beer pong tournament with multiple teams and games"""

    def __init__(self, name: str, tournament_id: str = None):
        self.id = tournament_id or str(uuid.uuid4())
        self.name = name
        self.teams: List[Team] = []
        self.games: List[Game] = []
        self.current_game: Optional[Game] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.winner: Optional[Team] = None
