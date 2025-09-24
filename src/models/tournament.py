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
        self.rounds: List[List[Game]] = []
        self.current_game: Optional[Game] = None
        self.current_round_index: Optional[int] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.winner: Optional[Team] = None


    def add_team(self, team: Team) -> None:
        """Add a team to the tournament"""
        self.teams.append(team)


    def start_tournament(self) -> None:
        """Mark tournament as started"""
        self.started_at = datetime.now()


    def schedule_round_robin(self) -> None:
        """Generate a round-robin schedule where every team plays each other once."""
        total_teams = len(self.teams)


        # Use a copy so we do not mutate the original order of teams
        rotating_teams: List[Optional[Team]] = self.teams.copy()

        # For an odd number of teams, add a dummy bye slot
        if total_teams % 2 == 1:
            rotating_teams.append(None)

        matchups_per_round = len(rotating_teams) // 2
        rounds: List[List[Game]] = []

        for _ in range(len(rotating_teams) - 1):
            round_games: List[Game] = []

            for match_index in range(matchups_per_round):
                team1 = rotating_teams[match_index]
                team2 = rotating_teams[-(match_index + 1)]

                if team1 is None or team2 is None:
                    # Bye week, skip creating a game
                    continue

                round_games.append(Game(team1, team2))

            rounds.append(round_games)

            # Rotate teams for next round while keeping the first team fixed
            rotating_teams = [
                rotating_teams[0],
                rotating_teams[-1],
                *rotating_teams[1:-1],
            ]

        self.rounds = rounds
        self.games = [game for round_games in rounds for game in round_games]
        self.current_round_index = 0 if rounds else None
        self.current_game = rounds[0][0] if rounds and rounds[0] else None
