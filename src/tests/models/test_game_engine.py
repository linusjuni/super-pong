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
