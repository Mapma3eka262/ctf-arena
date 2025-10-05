from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Team, TeamInvite
from app.schemas.team import TeamResponse, TeamWithMembers, InviteRequest, InviteResponse
from app.services.invitation_service import InvitationService

router = APIRouter()

@router.get("/my", response_model=TeamWithMembers)
async def get_my_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о команде пользователя"""
    if not current_user.team:
        raise HTTPException(status_code=404, detail="User not in a team")
    
    return current_user.team

@router.get("/ranking", response_model=List[dict])
async def get_teams_ranking(
    db: Session = Depends(get_db)
):
    """Рейтинг команд"""
    teams = db.query(Team).filter(Team.is_active == True).order_by(Team.score.desc()).all()
    
    ranking = []
    for rank, team in enumerate(teams, 1):
        # Подсчет решенных заданий
        solved_challenges = len(set(
            submission.challenge_id 
            for submission in team.submissions 
            if submission.status == 'accepted'
        ))
        
        ranking.append({
            "rank": rank,
            "team": {
                "id": team.id,
                "name": team.name,
                "score": team.score
            },
            "solved_challenges": solved_challenges
        })
    
    return ranking

@router.post("/invites", response_model=InviteResponse)
async def invite_member(
    invite_data: InviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Приглашение участника в команду (только капитан)"""
    if current_user.role != 'captain':
        raise HTTPException(status_code=403, detail="Only team captain can invite members")
    
    if not current_user.team:
        raise HTTPException(status_code=404, detail="User not in a team")
    
    return InvitationService.create_invitation(db, current_user.team.id, current_user.id, invite_data.email)

@router.get("/invites", response_model=List[InviteResponse])
async def get_team_invites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Список приглашений команды"""
    if current_user.role != 'captain':
        raise HTTPException(status_code=403, detail="Only team captain can view invites")
    
    if not current_user.team:
        raise HTTPException(status_code=404, detail="User not in a team")
    
    invites = db.query(TeamInvite).filter(
        TeamInvite.team_id == current_user.team.id
    ).order_by(TeamInvite.created_at.desc()).all()
    
    return [
        {
            "id": invite.id,
            "email": invite.email,
            "status": invite.status,
            "expires_at": invite.expires_at,
            "invited_by": invite.inviter.username
        }
        for invite in invites
    ]

@router.post("/invites/{token}/accept")
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принятие приглашения в команду"""
    return InvitationService.accept_invitation(db, token, current_user.id)

@router.delete("/invites/{invite_id}")
async def cancel_invitation(
    invite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отмена приглашения"""
    if current_user.role != 'captain':
        raise HTTPException(status_code=403, detail="Only team captain can cancel invites")
    
    invite = db.query(TeamInvite).filter(
        TeamInvite.id == invite_id,
        TeamInvite.team_id == current_user.team_id
    ).first()
    
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    db.delete(invite)
    db.commit()
    
    return {"message": "Invitation cancelled"}