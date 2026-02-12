from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Game, GameCreate, GamePublic, GameUpdate, Tournament

router = APIRouter(tags=["games"])


@router.post("/tournaments/{tournament_id}/games", response_model=GamePublic, status_code=201)
def create_game(
    tournament_id: int,
    body: GameCreate,
    session: Session = Depends(get_session),
):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    game = Game(tournament_id=tournament_id, **body.model_dump())
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@router.get("/tournaments/{tournament_id}/games", response_model=list[GamePublic])
def list_games(tournament_id: int, session: Session = Depends(get_session)):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    return session.exec(
        select(Game).where(Game.tournament_id == tournament_id)
    ).all()


@router.get("/games/{game_id}", response_model=GamePublic)
def get_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    return game


@router.put("/games/{game_id}", response_model=GamePublic)
def update_game(
    game_id: int,
    body: GameUpdate,
    session: Session = Depends(get_session),
):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(game, key, value)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@router.delete("/games/{game_id}", status_code=204)
def delete_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    session.delete(game)
    session.commit()
