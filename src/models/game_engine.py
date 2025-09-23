from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from .game import Game, GameState, ShotType, ShotOutcome, Shot
from .team import Team
from .player import Player


@dataclass
class ShotData:
    """Input data for a single shot."""

    player: Player
    shot_type: ShotType
    outcome: ShotOutcome
    elbow_violation: bool = False
    cup_position: Optional[str] = None
    bounces: Optional[int] = None


@dataclass
class TurnRecord:
    """Record of a complete turn for analytics and debugging."""

    turn_number: int
    team: Team
    player1_shot: Shot
    player2_shot: Shot
    cups_removed: int
    balls_back: bool
    two_balls_one_cup: bool
    special_events: List[str]
    timestamp: datetime


@dataclass
class TurnResult:
    """Result of processing a complete turn (2 shots)."""

    # Success/Error status
    success: bool
    error_message: Optional[str] = None

    # Turn tracking
    shots_recorded: int = 0
    total_cups_removed: int = 0
    individual_hits: int = 0

    # Special conditions
    balls_back: bool = False
    two_balls_one_cup: bool = False
    special_events: List[str] = None

    # Turn management
    turn_continues: bool = False  # True if same team gets another turn
    next_team_name: Optional[str] = None
    suggested_starting_player: Optional[str] = None  # UI suggestion only

    # Current game state
    team1_cups_remaining: int = 0
    team2_cups_remaining: int = 0

    # Game completion
    game_over: bool = False
    winner_name: Optional[str] = None

    def __post_init__(self):
        if self.special_events is None:
            self.special_events = []


class GameEngine:
    """Central controller for managing game flow and state."""

    def __init__(self, game: Game):
        self.game = game

        # Turn tracking
        self.turn_number: int = 0
        self.turn_history: List[TurnRecord] = []

        # Balls back tracking
        self.is_balls_back_turn: bool = False
        self.consecutive_balls_back: int = 0

        # Redemption tracking (for future implementation)
        self.is_redemption_round: bool = False
        self.redemption_shots_taken: int = 0
        self.redemption_team: Optional[Team] = None
        self.redemption_hits_needed: int = 0

    def process_turn(self, shot1: ShotData, shot2: ShotData) -> TurnResult:
        """
        Process a complete turn (2 shots) with flexible player selection.
        Teams can choose which players take shots within their turn.
        """
        # Validate that we can take a turn
        if self.game.state != GameState.IN_PROGRESS:
            return TurnResult(success=False, error_message="Game is not in progress")

        # Validate that both players belong to the current team
        validation_error = self._validate_players_for_turn(shot1.player, shot2.player)
        if validation_error:
            return TurnResult(success=False, error_message=validation_error)

        # Increment turn number
        self.turn_number += 1

        # Record both shots with validation
        shots_recorded = 0
        recorded_shots = []

        # Record shot 1
        try:
            shot1_record = self._record_shot(shot1, shot1.player)
            shots_recorded += 1
            recorded_shots.append((shot1, shot1_record))
        except ValueError as e:
            return TurnResult(success=False, error_message=f"Shot 1 error: {str(e)}")

        # Record shot 2
        try:
            shot2_record = self._record_shot(shot2, shot2.player)
            shots_recorded += 1
            recorded_shots.append((shot2, shot2_record))
        except ValueError as e:
            return TurnResult(success=False, error_message=f"Shot 2 error: {str(e)}")

        # Update player stats for both players
        shot1.player.total_shots_taken += 1
        shot2.player.total_shots_taken += 1

        # Analyze the complete turn
        turn_analysis = self._analyze_turn([shot1, shot2])

        # Calculate total cups to remove based on special conditions
        total_cups_removed = self._calculate_cups_removed(turn_analysis)

        # Update player stats for successful cups
        self._update_player_cup_stats(shot1, shot2, total_cups_removed, turn_analysis)

        # Remove cups from opposing team
        if total_cups_removed > 0:
            if self.game.current_team == self.game.team1:
                self.game.team2_cups_remaining = max(
                    0, self.game.team2_cups_remaining - total_cups_removed
                )
            else:
                self.game.team1_cups_remaining = max(
                    0, self.game.team1_cups_remaining - total_cups_removed
                )

        # Record turn in history
        turn_record = TurnRecord(
            turn_number=self.turn_number,
            team=self.game.current_team,
            player1_shot=recorded_shots[0][1],
            player2_shot=recorded_shots[1][1],
            cups_removed=total_cups_removed,
            balls_back=turn_analysis.balls_back,
            two_balls_one_cup=turn_analysis.two_balls_one_cup,
            special_events=turn_analysis.special_events.copy(),
            timestamp=datetime.now(),
        )
        self.turn_history.append(turn_record)

        # Check for game over
        if self.check_game_over():
            return TurnResult(
                success=True,
                shots_recorded=shots_recorded,
                total_cups_removed=total_cups_removed,
                individual_hits=turn_analysis.individual_hits,
                balls_back=turn_analysis.balls_back,
                two_balls_one_cup=turn_analysis.two_balls_one_cup,
                special_events=turn_analysis.special_events,
                team1_cups_remaining=self.game.team1_cups_remaining,
                team2_cups_remaining=self.game.team2_cups_remaining,
                game_over=True,
                winner_name=self.game.winner.name,
            )

        # Handle turn continuation or switching
        turn_continues = turn_analysis.balls_back or turn_analysis.two_balls_one_cup

        if turn_continues:
            # Same team continues
            self.consecutive_balls_back += 1
            self.is_balls_back_turn = True
            # current_player remains a suggestion - teams can choose any player
        else:
            # Switch to other team
            self._switch_to_other_team()
            self.consecutive_balls_back = 0
            self.is_balls_back_turn = False

        return TurnResult(
            success=True,
            shots_recorded=shots_recorded,
            total_cups_removed=total_cups_removed,
            individual_hits=turn_analysis.individual_hits,
            balls_back=turn_analysis.balls_back,
            two_balls_one_cup=turn_analysis.two_balls_one_cup,
            special_events=turn_analysis.special_events,
            turn_continues=turn_continues,
            next_team_name=self.game.current_team.name,
            suggested_starting_player=self.game.current_player.name,  # Just a suggestion
            team1_cups_remaining=self.game.team1_cups_remaining,
            team2_cups_remaining=self.game.team2_cups_remaining,
            game_over=False,
        )

    def _validate_players_for_turn(
        self, player1: Player, player2: Player
    ) -> Optional[str]:
        """
        Validate that the specified players can take shots for the current team.
        Returns error message if invalid, None if valid.
        """
        current_team_players = [
            self.game.current_team.player1,
            self.game.current_team.player2,
        ]

        # Check that both players belong to current team
        if player1 not in current_team_players:
            return f"Player {player1.name} is not on the current team ({self.game.current_team.name})"

        if player2 not in current_team_players:
            return f"Player {player2.name} is not on the current team ({self.game.current_team.name})"

        # We allow the same player to take both shots if teams choose to do so
        # Only in the codebase though. In reality, teams should alternate players!
        return None  # Valid

    def _update_player_cup_stats(
        self, shot1: ShotData, shot2: ShotData, total_cups_removed: int, turn_analysis
    ) -> None:
        """Update player statistics for cups hit, using actual players from shots."""
        if total_cups_removed == 0:
            return

        # Calculate individual cups each player would have hit without special rules
        player1_individual_cups = self._get_individual_cups_hit(shot1)
        player2_individual_cups = self._get_individual_cups_hit(shot2)

        if turn_analysis.balls_back or turn_analysis.two_balls_one_cup:
            # For special conditions, distribute the cups based on who contributed
            total_individual_cups = player1_individual_cups + player2_individual_cups

            if total_individual_cups > 0:
                # Distribute extra cups proportionally to individual contribution
                extra_cups = total_cups_removed - total_individual_cups

                if player1_individual_cups > 0:
                    # Give player1 their individual cups plus proportional share of bonus
                    player1_bonus = extra_cups * (
                        player1_individual_cups / total_individual_cups
                    )
                    shot1.player.total_cups_hit += player1_individual_cups + int(
                        player1_bonus
                    )

                if player2_individual_cups > 0:
                    # Give player2 their individual cups plus remaining bonus
                    player2_bonus = extra_cups * (
                        player2_individual_cups / total_individual_cups
                    )
                    shot2.player.total_cups_hit += player2_individual_cups + int(
                        player2_bonus
                    )
        else:
            # Regular case: each player gets credit for their individual hits
            shot1.player.total_cups_hit += player1_individual_cups
            shot2.player.total_cups_hit += player2_individual_cups

    @dataclass
    class _TurnAnalysis:
        """Internal analysis of a turn."""

        individual_hits: int
        balls_back: bool
        two_balls_one_cup: bool
        same_cup_hits: bool
        bounce_cups: int
        special_events: List[str]

    def _analyze_turn(self, shots: List[ShotData]) -> _TurnAnalysis:
        """Analyze the two shots to determine special conditions."""
        individual_hits = 0
        bounce_cups = 0
        special_events = []
        same_cup_hits = False

        # Check each shot individually
        hit_positions = []
        for shot in shots:
            if self._is_individual_hit(shot):
                individual_hits += 1
                if shot.cup_position:
                    hit_positions.append(shot.cup_position)

            # Calculate bounce cups (bounces + 1 for each bounce shot that hits)
            if shot.shot_type == ShotType.BOUNCE and self._is_individual_hit(shot):
                bounce_cups += (shot.bounces or 0) + 1

        # Check for two balls one cup (both hit the same cup position)
        two_balls_one_cup = (
            len(hit_positions) == 2
            and len(set(hit_positions)) == 1
            and hit_positions[0] is not None
        )

        # Check for balls back (both shots hit individually)
        balls_back = individual_hits == 2

        # Determine special events
        if two_balls_one_cup:
            special_events.append("two_balls_one_cup")
        elif balls_back:  # Only balls_back if not two_balls_one_cup
            special_events.append("balls_back")

        return self._TurnAnalysis(
            individual_hits=individual_hits,
            balls_back=balls_back
            and not two_balls_one_cup,  # Two balls one cup overrides balls back
            two_balls_one_cup=two_balls_one_cup,
            same_cup_hits=same_cup_hits,
            bounce_cups=bounce_cups,
            special_events=special_events,
        )

    def _calculate_cups_removed(self, analysis: _TurnAnalysis) -> int:
        """Calculate total cups to remove based on turn analysis."""
        if analysis.two_balls_one_cup:
            # Two balls one cup: 3 cups total
            return 3
        elif analysis.balls_back:
            # Balls back: 2 cups total
            return 2
        else:
            # Regular case: individual hits + bounce bonuses
            regular_hits = analysis.individual_hits
            bounce_bonus = (
                analysis.bounce_cups - analysis.individual_hits
            )  # Extra cups from bounces
            return regular_hits + bounce_bonus

    def _is_individual_hit(self, shot: ShotData) -> bool:
        """Determine if an individual shot counts as a hit."""
        # Elbow violation negates any hit
        if shot.elbow_violation:
            return False

        # For normal and trick shots, only HIT outcome counts
        if shot.shot_type in [ShotType.NORMAL, ShotType.TRICKSHOT]:
            return shot.outcome == ShotOutcome.HIT

        # For bounce shots, must have bounces > 0 regardless of outcome
        if shot.shot_type == ShotType.BOUNCE:
            return shot.bounces is not None and shot.bounces > 0

        return False

    def _get_individual_cups_hit(self, shot: ShotData) -> int:
        """Get the number of cups this individual shot would remove (without special conditions)."""
        if not self._is_individual_hit(shot):
            return 0

        if shot.shot_type == ShotType.BOUNCE and shot.bounces:
            return shot.bounces + 1  # Bounce rule: bounces + 1 cups
        else:
            return 1  # Normal hit

    def _record_shot(self, shot_data: ShotData, player: Player) -> Shot:
        """Record a single shot with validation. Returns the created Shot object."""
        # Validate bounce shot requirements
        if shot_data.shot_type == ShotType.BOUNCE:
            if shot_data.bounces is None or shot_data.bounces <= 0:
                raise ValueError("Bounce shots must have bounces > 0")
        else:
            if shot_data.bounces is not None:
                raise ValueError(
                    f"Only bounce shots can have bounces, got {shot_data.shot_type.value} with bounces={shot_data.bounces}"
                )

        shot = Shot(
            player_name=player.name,
            team_name=self.game.current_team.name,
            shot_type=shot_data.shot_type,
            outcome=shot_data.outcome,
            timestamp=datetime.now(),
            elbow_violation=shot_data.elbow_violation,
            cup_position=shot_data.cup_position,
            bounces=shot_data.bounces
            if shot_data.shot_type == ShotType.BOUNCE
            else None,
        )
        self.game.shots.append(shot)
        return shot

    def _switch_to_other_team(self) -> None:
        """
        Switch to the other team. current_player becomes a UI suggestion only.
        Teams have complete flexibility in choosing which players take shots.
        """
        self.game.current_team = (
            self.game.team2
            if self.game.current_team == self.game.team1
            else self.game.team1
        )
        # Set suggested starting player - UI can override this completely
        self.game.current_player = self.game.current_team.player1

    def get_current_team_players(self) -> List[Player]:
        """
        Get the list of players who can take shots for the current team.
        Useful for UI to populate player selection.
        """
        return [self.game.current_team.player1, self.game.current_team.player2]

    def get_suggested_starting_player(self) -> Player:
        """
        Get the suggested starting player for the current team.
        UI can use this as a default but override if needed.
        """
        return self.game.current_player

    def get_opposing_team(self) -> Team:
        """Get the team that is not currently taking shots."""
        return (
            self.game.team2
            if self.game.current_team == self.game.team1
            else self.game.team1
        )

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

    def check_game_over(self) -> bool:
        """Check if the game is over and set winner if so"""
        if self.game.team1_cups_remaining <= 0:
            self.end_game(self.game.team1)
            return True
        elif self.game.team2_cups_remaining <= 0:
            self.end_game(self.game.team2)
            return True
        return False

    def add_beer_bong(self, team: Team) -> None:
        """Add a beer bong for the specified team"""
        if team == self.game.team1:
            self.game.team1_beer_bongs += 1
        else:
            self.game.team2_beer_bongs += 1

    def get_current_player(self) -> Player:
        """
        Get the current suggested player.
        Note: This is just a suggestion - teams can choose any valid player.
        """
        return self.game.current_player

    def get_turn_history(self) -> List[TurnRecord]:
        """Get the complete turn history for analytics."""
        return self.turn_history.copy()

    def _get_game_duration(self) -> Optional[float]:
        """Get game duration in minutes"""
        if self.game.start_time:
            end_time = self.game.end_time or datetime.now()
            duration = end_time - self.game.start_time
            return duration.total_seconds() / 60
        return None
