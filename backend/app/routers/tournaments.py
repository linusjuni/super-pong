from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    DashboardStats,
    Tournament,
    TournamentCreate,
    TournamentPublic,
    TournamentStats,
)
from ..stats import get_dashboard, get_tournament_stats

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
def tournament_stats(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    return get_tournament_stats(session, tournament.id, tournament.name)


@router.get("/{tournament_id}/dashboard", response_model=DashboardStats)
def tournament_dashboard(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    return get_dashboard(session, tournament.id, tournament.name)
