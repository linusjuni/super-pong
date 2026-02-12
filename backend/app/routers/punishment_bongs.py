from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    PunishmentBong,
    PunishmentBongCreate,
    PunishmentBongPublic,
    Tournament,
    Player,
)

router = APIRouter(tags=["punishment-bongs"])


@router.post(
    "/tournaments/{tournament_id}/punishment-bongs",
    response_model=PunishmentBongPublic,
    status_code=201,
)
def create_punishment_bong(
    tournament_id: int,
    body: PunishmentBongCreate,
    session: Session = Depends(get_session),
):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    if not session.get(Player, body.player_id):
        raise HTTPException(404, "Player not found")
    pb = PunishmentBong(tournament_id=tournament_id, **body.model_dump())
    session.add(pb)
    session.commit()
    session.refresh(pb)
    return pb


@router.get(
    "/tournaments/{tournament_id}/punishment-bongs",
    response_model=list[PunishmentBongPublic],
)
def list_punishment_bongs(
    tournament_id: int, session: Session = Depends(get_session)
):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    return session.exec(
        select(PunishmentBong)
        .where(PunishmentBong.tournament_id == tournament_id)
        .order_by(PunishmentBong.timestamp.desc())
    ).all()


@router.delete("/punishment-bongs/{punishment_bong_id}", status_code=204)
def delete_punishment_bong(
    punishment_bong_id: int, session: Session = Depends(get_session)
):
    pb = session.get(PunishmentBong, punishment_bong_id)
    if not pb:
        raise HTTPException(404, "Punishment bong not found")
    session.delete(pb)
    session.commit()
