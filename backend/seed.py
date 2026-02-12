"""Seed script: creates SuperPongTest tournament with 10 teams in 2 groups.

Usage:
    cd backend
    uv run python seed.py
"""

from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.models import Game, Player, Team, Tournament

TOURNAMENT_NAME = "SuperPongTest"

GROUPS = {
    "A": [
        ("Ali", "Kasper"),
        ("Florenz", "Oskar"),
        ("Markus", "Aksel"),
        ("Satya", "Mathilde"),
        ("Meier", "Lauge"),
    ],
    "B": [
        ("Linus", "Theo"),
        ("Andreas", "Martin"),
        ("Ryan", "Himmer"),
        ("Daniel", "Oscar"),
        ("Carl", "Booze"),
    ],
}


def seed():
    create_db_and_tables()

    with Session(engine) as session:
        # --- Players (get or create) ---
        player_cache: dict[str, Player] = {}
        for pairs in GROUPS.values():
            for p1_name, p2_name in pairs:
                for name in (p1_name, p2_name):
                    if name not in player_cache:
                        player = Player(name=name)
                        session.add(player)
                        session.flush()  # get id
                        player_cache[name] = player

        # --- Tournament ---
        tournament = Tournament(name=TOURNAMENT_NAME)
        session.add(tournament)
        session.flush()

        # --- Teams ---
        all_teams: dict[str, list[Team]] = {}
        for group, pairs in GROUPS.items():
            all_teams[group] = []
            for p1_name, p2_name in pairs:
                team = Team(
                    name=f"{p1_name} & {p2_name}",
                    player1_id=player_cache[p1_name].id,
                    player2_id=player_cache[p2_name].id,
                    tournament_id=tournament.id,
                    group=group,
                )
                session.add(team)
                session.flush()
                all_teams[group].append(team)

        # --- Round-robin games within each group ---
        for group, teams in all_teams.items():
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    game = Game(
                        tournament_id=tournament.id,
                        team1_id=teams[i].id,
                        team2_id=teams[j].id,
                        starting_cups_per_team=6,
                    )
                    session.add(game)

        session.commit()

        total_games = sum(
            len(teams) * (len(teams) - 1) // 2 for teams in all_teams.values()
        )
        print(f"✓ Tournament '{TOURNAMENT_NAME}' (id={tournament.id})")
        print(
            f"  {len(player_cache)} players, {sum(len(t) for t in all_teams.values())} teams, {total_games} games"
        )


if __name__ == "__main__":
    seed()
