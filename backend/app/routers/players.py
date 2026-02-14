from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import Player, PlayerCreate, PlayerPublic, PlayerStats
from ..stats import get_player_stats

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
def player_stats(player_id: int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    return get_player_stats(session, player.id, player.name)
