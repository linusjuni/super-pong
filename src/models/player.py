from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class GameStats:
    """Individual game statistics for a player"""

    game_id: str
    cups_hit: int
    shots_taken: int
    beer_bongs_drunk: int
    date: datetime


class Player:
    def __init__(self, name: str):
        self.name = name
        self.total_cups_hit = 0
        self.total_shots_taken = 0
        self.total_beer_bongs_drunk = 0
        self.game_stats: List[GameStats] = []  # Per-game statistics
        self.created_at = datetime.now()
