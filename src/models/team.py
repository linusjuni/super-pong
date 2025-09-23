# models/team.py
from typing import List, Optional
from datetime import datetime
from .player import Player


class Team:
    def __init__(self, player1: Player, player2: Player, name: Optional[str] = None):
        self.player1 = player1
        self.player2 = player2
        self.name = name or f"{player1.name} & {player2.name}"

        # Team statistics
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.games_played: List[str] = []  # List of game IDs
        self.created_at = datetime.now()
    
    @property
    def players(self) -> List[Player]:
        """Get both players as a list"""
        return [self.player1, self.player2]
