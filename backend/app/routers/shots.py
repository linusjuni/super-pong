from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Game, Shot, ShotCreate, ShotPublic

router = APIRouter(tags=["shots"])


@router.post("/games/{game_id}/shots", response_model=ShotPublic, status_code=201)
def create_shot(
    game_id: int,
    body: ShotCreate,
    session: Session = Depends(get_session),
):
    if not session.get(Game, game_id):
        raise HTTPException(404, "Game not found")
    shot = Shot(game_id=game_id, **body.model_dump())
    session.add(shot)
    session.commit()
    session.refresh(shot)
    return shot


@router.get("/games/{game_id}/shots", response_model=list[ShotPublic])
def list_shots(game_id: int, session: Session = Depends(get_session)):
    if not session.get(Game, game_id):
        raise HTTPException(404, "Game not found")
    return session.exec(
        select(Shot).where(Shot.game_id == game_id).order_by(Shot.timestamp.desc())
    ).all()


@router.delete("/shots/{shot_id}", status_code=204)
def delete_shot(shot_id: int, session: Session = Depends(get_session)):
    shot = session.get(Shot, shot_id)
    if not shot:
        raise HTTPException(404, "Shot not found")
    session.delete(shot)
    session.commit()
