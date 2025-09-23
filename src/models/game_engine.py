from typing import Optional
from datetime import datetime
from .game import Game, GameState, ShotType, ShotOutcome, Shot
from .team import Team
from .player import Player


class GameEngine:
    """Central controller for managing game flow and state."""

    def __init__(self, game: Game):
        self.game = game

        # Turn tracking
        self.shots_this_turn: int = 0
        self.max_shots_per_turn: int = 2
        self.hits_this_turn: int = 0

        # Balls back tracking
        self.is_balls_back_turn: bool = False
        self.consecutive_balls_back: int = 0

        # Redemption tracking
        self.is_redemption_round: bool = False
        self.redemption_shots_taken: int = 0
        self.redemption_team: Optional[Team] = None
        self.redemption_hits_needed: int = 0

    def get_current_player(self) -> Player:
        """Get the current player object"""
        return self.game.current_player
    
    def get_other_team(self) -> Team:
        """Get the team that is not currently playing"""
        return self.game.team2 if self.game.current_team == self.game.team1 else self.game.team1
    
    def switch_to_next_player(self) -> None:
        """
        Both players on a team shoot, then the turn switches to the other team.
        """
        match self.game.current_player:
            case self.game.current_team.player1:
                self.game.current_player = self.game.current_team.player2
            case self.game.current_team.player2:
                self.game.current_team = self.get_other_team()
                self.game.current_player = self.game.current_team.player1
            case _:
                raise ValueError("Current player is not part of the current team.")
    
    def start_game(self) -> None:
        """Start the game"""
        self.game.state = GameState.IN_PROGRESS
        self.game.start_time = datetime.now()
    
    def end_game(self, winner: Team) -> None:
        """End the game with a winner"""
        self.game.state = GameState.FINISHED
        self.game.winner = winner
        self.game.end_time = datetime.now()
    
    def pause_game(self) -> None:
        """Pause the game"""
        self.game.state = GameState.PAUSED
    
    def resume_game(self) -> None:
        """Resume a paused game"""
        if self.game.state == GameState.PAUSED:
            self.game.state = GameState.IN_PROGRESS
    
    def record_shot(
        self,
        shot_type: ShotType,
        outcome: ShotOutcome,
        elbow_violation: bool = False,
        cup_position: Optional[str] = None,
        bounces: Optional[int] = None
    ) -> None:
        """Record a shot taken by the current player, with type and outcome"""
        shot = Shot(
            player_name=self.game.current_player.name,
            team_name=self.game.current_team.name,
            shot_type=shot_type,
            outcome=outcome,
            timestamp=datetime.now(),
            elbow_violation=elbow_violation,
            cup_position=cup_position,
            bounces=bounces if shot_type == ShotType.BOUNCE else None
        )
        self.game.shots.append(shot)

        # Update cups remaining if shot went in (outcome == HIT) and not elbow violation
        pass
    
    def check_game_over(self) -> bool:
        """Check if the game is over and set winner if so"""
        if self.game.team1_cups_remaining <= 0:
            self.end_game(self.game.team1)
            return True
        elif self.game.team2_cups_remaining <= 0:
            self.end_game(self.game.team2)
            return True
        return False
    
    def is_turn_complete(self) -> bool:
        """Check if the current turn is complete"""
        return self.shots_this_turn >= self.max_shots_per_turn
    
    def end_turn(self) -> None:
        """End the current turn and reset counters"""
        # Check for balls back (both shots hit)
        if self.hits_this_turn == 2:
            self.is_balls_back_turn = True
            self.consecutive_balls_back += 1
        else:
            self.is_balls_back_turn = False
            self.consecutive_balls_back = 0
            # Switch to the other team if no balls back
            self.switch_to_next_player()
        
        # Reset turn counters
        self.shots_this_turn = 0
        self.hits_this_turn = 0
    
    def add_beer_bong(self, team: Team) -> None:
        """Add a beer bong for the specified team"""
        if team == self.game.team1:
            self.game.team1_beer_bongs += 1
        else:
            self.game.team2_beer_bongs += 1
    
    def _get_game_duration(self) -> Optional[float]:
        """Get game duration in minutes"""
        if self.game.start_time:
            end_time = self.game.end_time or datetime.now()
            duration = end_time - self.game.start_time
            return duration.total_seconds() / 60
        return None
