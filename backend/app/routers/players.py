from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlmodel import Session, select

from ..database import get_session
from ..models import Player, PlayerCreate, PlayerPublic, PlayerStats

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=list[PlayerPublic])
def list_players(session: Session = Depends(get_session)):
    return session.exec(select(Player).order_by(Player.name)).all()


@router.get("/search", response_model=list[PlayerPublic])
def search_players(
    q: str = Query(min_length=1),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(Player).where(Player.name.ilike(f"%{q}%")).order_by(Player.name)
    ).all()


@router.post("/", response_model=PlayerPublic, status_code=201)
def create_player(body: PlayerCreate, session: Session = Depends(get_session)):
    player = Player.model_validate(body)
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


@router.get("/{player_id}", response_model=PlayerPublic)
def get_player(player_id: int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    return player


@router.get("/{player_id}/stats", response_model=PlayerStats)
def get_player_stats(player_id: int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")

    row = session.execute(
        text("""
            SELECT
                COUNT(*)                                             AS total_shots,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END)   AS hits,
                SUM(CASE WHEN outcome = 'MISS' THEN 1 ELSE 0 END)  AS misses,
                SUM(CASE WHEN outcome = 'RIM' THEN 1 ELSE 0 END)   AS rims,
                SUM(CASE WHEN shot_type = 'NORMAL' AND outcome = 'HIT' THEN 1 ELSE 0 END) AS normal_hits,
                SUM(CASE WHEN shot_type = 'NORMAL' THEN 1 ELSE 0 END)                     AS normal_total,
                SUM(CASE WHEN shot_type = 'BOUNCE' AND outcome = 'HIT' THEN 1 ELSE 0 END) AS bounce_hits,
                SUM(CASE WHEN shot_type = 'BOUNCE' THEN 1 ELSE 0 END)                     AS bounce_total,
                SUM(CASE WHEN shot_type = 'TRICKSHOT' AND outcome = 'HIT' THEN 1 ELSE 0 END) AS trickshot_hits,
                SUM(CASE WHEN shot_type = 'TRICKSHOT' THEN 1 ELSE 0 END)                     AS trickshot_total,
                SUM(CASE WHEN elbow_violation = 1 THEN 1 ELSE 0 END) AS elbow_violations
            FROM shot
            WHERE player_id = :pid AND shot_type != 'RERACK'
        """),
        {"pid": player_id},
    ).one()

    total = row.total_shots or 0
    hits = row.hits or 0

    return PlayerStats(
        player_id=player.id,
        player_name=player.name,
        total_shots=total,
        hits=hits,
        misses=row.misses or 0,
        rims=row.rims or 0,
        hit_percentage=round(hits / total * 100, 1) if total > 0 else 0.0,
        normal_hits=row.normal_hits or 0,
        normal_total=row.normal_total or 0,
        bounce_hits=row.bounce_hits or 0,
        bounce_total=row.bounce_total or 0,
        trickshot_hits=row.trickshot_hits or 0,
        trickshot_total=row.trickshot_total or 0,
        elbow_violations=row.elbow_violations or 0,
    )
