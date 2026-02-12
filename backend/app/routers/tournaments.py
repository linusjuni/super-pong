from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Game,
    GameStatus,
    PlayerLeaderboardEntry,
    Team,
    TeamStanding,
    Tournament,
    TournamentCreate,
    TournamentPublic,
    TournamentStats,
)

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("/", response_model=list[TournamentPublic])
def list_tournaments(session: Session = Depends(get_session)):
    return session.exec(select(Tournament).order_by(Tournament.created_at.desc())).all()


@router.post("/", response_model=TournamentPublic, status_code=201)
def create_tournament(body: TournamentCreate, session: Session = Depends(get_session)):
    tournament = Tournament.model_validate(body)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.get("/{tournament_id}", response_model=TournamentPublic)
def get_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    return tournament


@router.delete("/{tournament_id}", status_code=204)
def delete_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    session.delete(tournament)
    session.commit()


@router.get("/{tournament_id}/stats", response_model=TournamentStats)
def get_tournament_stats(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(404, "Tournament not found")

    total_games = len(session.exec(
        select(Game).where(Game.tournament_id == tournament_id)
    ).all())
    completed_games = len(session.exec(
        select(Game).where(Game.tournament_id == tournament_id, Game.status == GameStatus.COMPLETED)
    ).all())

    # Player leaderboard: all players who shot in this tournament's games
    leaderboard_rows = session.execute(
        text("""
            SELECT
                p.id   AS player_id,
                p.name AS player_name,
                COUNT(*)                                           AS total_shots,
                SUM(CASE WHEN s.outcome = 'HIT' THEN 1 ELSE 0 END) AS hits
            FROM shot s
            JOIN game g ON s.game_id = g.id
            JOIN player p ON s.player_id = p.id
            WHERE g.tournament_id = :tid AND s.shot_type != 'RERACK'
            GROUP BY p.id
            ORDER BY hits DESC, total_shots ASC
        """),
        {"tid": tournament_id},
    ).all()

    leaderboard = [
        PlayerLeaderboardEntry(
            player_id=r.player_id,
            player_name=r.player_name,
            total_shots=r.total_shots,
            hits=r.hits,
            hit_percentage=round(r.hits / r.total_shots * 100, 1) if r.total_shots > 0 else 0.0,
        )
        for r in leaderboard_rows
    ]

    # Team standings with W-L records
    standing_rows = session.execute(
        text("""
            SELECT
                t.id   AS team_id,
                t.name AS team_name,
                p1.name AS player1_name,
                p2.name AS player2_name,
                SUM(CASE WHEN g.winner_id = t.id THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN g.winner_id IS NOT NULL AND g.winner_id != t.id THEN 1 ELSE 0 END) AS losses,
                COUNT(g.id) AS games_played
            FROM team t
            JOIN player p1 ON t.player1_id = p1.id
            JOIN player p2 ON t.player2_id = p2.id
            LEFT JOIN game g ON (g.team1_id = t.id OR g.team2_id = t.id)
                AND g.status = 'COMPLETED'
            WHERE t.tournament_id = :tid
            GROUP BY t.id
            ORDER BY wins DESC, losses ASC
        """),
        {"tid": tournament_id},
    ).all()

    standings = [
        TeamStanding(
            team_id=r.team_id,
            team_name=r.team_name,
            player1_name=r.player1_name,
            player2_name=r.player2_name,
            wins=r.wins or 0,
            losses=r.losses or 0,
            games_played=r.games_played or 0,
        )
        for r in standing_rows
    ]

    return TournamentStats(
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        total_games=total_games,
        completed_games=completed_games,
        player_leaderboard=leaderboard,
        team_standings=standings,
    )
