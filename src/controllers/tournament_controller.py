from dataclasses import dataclass
from typing import List
from models.player import Player
from models.team import Team
from models.tournament import Tournament
from models.game_engine import GameEngine


@dataclass
class TeamData:
    """Simple data structure for team input data"""
    team_name: str
    player1_name: str
    player2_name: str
    locked: bool


class TournamentController:
    """Controller for managing tournament operations"""

    def __init__(self, app_state):
        self.app_state = app_state

    def create_tournament(self, teams_data: List[TeamData]) -> str:
        """Create a tournament with the provided teams data.

        Returns error message if validation fails, empty string if successful.
        """
        # Validation
        if len(teams_data) < 2:
            return "Need at least 2 teams to start tournament!"

        unlocked_teams = [team for team in teams_data if not team.locked]
        if unlocked_teams:
            return "Please lock in all teams before starting!"

        # Create the tournament
        tournament = Tournament("Super Pong Tournament")

        # Create Player and Team objects
        for team_data in teams_data:
            # Create player objects
            player1 = Player(team_data.player1_name)
            player2 = Player(team_data.player2_name)

            # Create team object
            team = Team(player1, player2, team_data.team_name)

            # Add team to tournament
            tournament.add_team(team)

        # Start the tournament
        tournament.start_tournament()
        tournament.schedule_round_robin()

        # Store in app state
        self.app_state.tournament = tournament
        if tournament.current_game:
            self.app_state.game = tournament.current_game
            self.app_state.engine = GameEngine(tournament.current_game)

        # Log success
        print(f"Successfully created tournament with {len(teams_data)} teams:")
        for team_data in teams_data:
            print(f"  Team: {team_data.team_name}")
            print(f"    Players: {team_data.player1_name}, {team_data.player2_name}")

        return None # Return None on success
