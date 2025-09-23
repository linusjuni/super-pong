from models.game import Game
from models.team import Team
from models.player import Player
from models.game_engine import GameEngine, ShotData, ShotType, ShotOutcome


def test_process_turn_fails_when_game_not_started():
    player_a = Player("A")
    player_b = Player("B")
    player_c = Player("C")
    player_d = Player("D")
    team1 = Team(player_a, player_b, name="Team1")
    team2 = Team(player_c, player_d, name="Team2")
    game = Game(team1, team2)
    engine = GameEngine(game)

    shot1 = ShotData(player=player_a, shot_type=ShotType.NORMAL, outcome=ShotOutcome.HIT)
    shot2 = ShotData(player=player_b, shot_type=ShotType.NORMAL, outcome=ShotOutcome.HIT)
    result = engine.process_turn(shot1, shot2)
    assert result.success is False
    assert result.error_message.lower() == "game is not in progress".lower()


def test_process_turn_success_balls_back_updates_state_and_stats():
    """
    Two normal hits -> balls_back -> should remove 2 cups, same team continues,
    players' total_shots_taken incremented and total_cups_hit updated.
    """

    player1 = Player("P1")
    player2 = Player("P2")
    player3 = Player("P3")
    player4 = Player("P4")
    team1 = Team(player1, player2, name="Team1")
    team2 = Team(player3, player4, name="Team2")
    game = Game(team1, team2)
    engine = GameEngine(game)

    # Start game
    engine.start_game()
    assert game.state.name == "IN_PROGRESS"

    # Record initial cups so we can assert deltas
    initial_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )

    # Both shots hit normally
    shot1 = ShotData(player=player1, shot_type=ShotType.NORMAL, outcome=ShotOutcome.HIT)
    shot2 = ShotData(player=player2, shot_type=ShotType.NORMAL, outcome=ShotOutcome.HIT)

    result = engine.process_turn(shot1, shot2)

    assert result.success is True, f"unexpected failure: {result.error_message}"
    assert result.shots_recorded == 2
    assert result.individual_hits == 2
    assert result.balls_back is True
    assert "balls_back" in (result.special_events or []) or result.balls_back is True

    # Cups removed should be 2 for balls back
    assert result.total_cups_removed == 2, "balls_back should remove exactly 2 cups"

    # Opponent's cups decreased by 2
    final_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )
    assert initial_opponent_cups - final_opponent_cups == 2

    # Each shooter should have one more shot taken
    assert player1.total_shots_taken >= 1
    assert player2.total_shots_taken >= 1

    # And they should be credited with cup hits (each at least 1)
    assert player1.total_cups_hit >= 1
    assert player2.total_cups_hit >= 1

    # Since balls_back -> turn continues, engine should not have switched teams
    # Next team name returned should be the same current team name
    assert result.turn_continues is True and result.balls_back is True
    assert engine.turn_history, "turn must be recorded in history"


def test_process_turn_two_balls_one_cup_distributes_and_marks_event():
    """
    Both shots hit the same cup position -> two_balls_one_cup special case:
    - should remove 3 cups
    - special_events should include 'two_balls_one_cup'
    - total_cups_hit distribution should reflect contributors
    """

    player_a = Player("A")
    player_b = Player("B")
    player_c = Player("C")
    player_d = Player("D")
    team1 = Team(player_a, player_b, name="Team1")
    team2 = Team(player_c, player_d, name="Team2")
    game = Game(team1, team2)
    engine = GameEngine(game)
    engine.start_game()

    initial_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )

    # Both shots hit the same cup position
    shot1 = ShotData(
        player=player_a,
        shot_type=ShotType.NORMAL,
        outcome=ShotOutcome.HIT,
        cup_position="CUP-1",
    )

    shot2 = ShotData(
        player=player_b,
        shot_type=ShotType.NORMAL,
        outcome=ShotOutcome.HIT,
        cup_position="CUP-1",
    )

    result = engine.process_turn(shot1, shot2)

    assert result.success is True
    assert result.two_balls_one_cup is True
    assert "two_balls_one_cup" in (result.special_events)
    assert result.total_cups_removed == 3

    # Opponent cups decreased by 3
    final_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )
    assert initial_opponent_cups - final_opponent_cups == 3

    # Players' cup stats should increase appropriately
    assert player_a.total_cups_hit >= 1.5
    assert player_b.total_cups_hit >= 1.5

    # History entry exists and references the two recorded shots
    assert engine.turn_history, "turn history should be non-empty"
    last_record = engine.turn_history[-1]
    assert last_record.cups_removed == 3
    assert last_record.team == game.current_team


def test_process_turn_bounce_shot_counts_bounce_rule():
    """
    Test a bounce shot: bounce with bounces=2 should count as 3 cups removed
    when the other shot misses.
    """
    p1 = Player("P1")
    p2 = Player("P2")
    p3 = Player("P3")
    p4 = Player("P4")
    t1 = Team(p1, p2, name="Team1")
    t2 = Team(p3, p4, name="Team2")
    game = Game(t1, t2)
    engine = GameEngine(game)
    engine.start_game()

    initial_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )

    # shot1 is a bounce with 2 bounces (should count as 3 cups), shot2 misses
    s1 = ShotData(
        player=p1, shot_type=ShotType.BOUNCE, outcome=ShotOutcome.MISS, bounces=2
    )
    s2 = ShotData(player=p2, shot_type=ShotType.NORMAL, outcome=ShotOutcome.MISS)

    res = engine.process_turn(s1, s2)
    assert res.success is True

    # Bounce rule: bounces + 1 => 3 cups removed
    assert res.total_cups_removed == 3, (
        f"expected 3 cups removed for bounce=2, got {res.total_cups_removed}"
    )
    final_opponent_cups = (
        game.team2_cups_remaining
        if game.current_team == game.team1
        else game.team1_cups_remaining
    )
    assert initial_opponent_cups - final_opponent_cups == 3
    # ensure player credited for cups from bounce
    assert p1.total_cups_hit >= 3 or p1.total_cups_hit >= 1, (
        "player should receive credit for bounce cups"
    )