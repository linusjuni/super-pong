from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Team, TeamCreate, TeamPublic, TeamUpdate, Tournament

router = APIRouter(tags=["teams"])


@router.post("/tournaments/{tournament_id}/teams", response_model=TeamPublic, status_code=201)
def create_team(
    tournament_id: int,
    body: TeamCreate,
    session: Session = Depends(get_session),
):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    team = Team(tournament_id=tournament_id, **body.model_dump())
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.get("/tournaments/{tournament_id}/teams", response_model=list[TeamPublic])
def list_teams(tournament_id: int, session: Session = Depends(get_session)):
    if not session.get(Tournament, tournament_id):
        raise HTTPException(404, "Tournament not found")
    return session.exec(
        select(Team).where(Team.tournament_id == tournament_id)
    ).all()


@router.put("/teams/{team_id}", response_model=TeamPublic)
def update_team(
    team_id: int,
    body: TeamUpdate,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(team, key, value)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/teams/{team_id}", status_code=204)
def delete_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    session.delete(team)
    session.commit()
