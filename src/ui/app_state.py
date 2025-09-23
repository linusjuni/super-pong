from dataclasses import dataclass
from typing import Optional
from models.game import Game
from models.game_engine import GameEngine
from models.tournament import Tournament


@dataclass
class AppState:
    game: Optional[Game] = None
    engine: Optional[GameEngine] = None
    tournament: Optional[Tournament] = None
