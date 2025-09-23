from dataclasses import dataclass
from models.game import Game
from models.game_engine import GameEngine
from models.tournament import Tournament


@dataclass
class AppState:
    game: Game | None = None
    engine: GameEngine | None = None
    tournament: Tournament | None = None
