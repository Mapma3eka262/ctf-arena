from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.team import Team
from app.models.invitation import Invitation
from app.schemas.invitation import TeamInvite  # Импорт из schemas
from app.services.invitation_service import InvitationService
from app.services.email_service import EmailService

router = APIRouter()

@router.get("/my")
async def get_my_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о команде пользователя"""
    if not current_user.team:
        raise HTTPException(status_code=404, detail="Пользователь не состоит в команде")
    
    team = current_user.team
    return {
        "id": team.id,
        "name": team.name,
        "score": team.score,
        "created_at": team.created_at,
        "members": [
            {
                "id": member.id,
                "username": member.username,
                "email": member.email,
                "role": "captain" if member.is_captain else "member",
                "is_active": member.is_active,
                "joined_at": member.joined_at
            }
            for member in team.members
        ]
    }

@router.post("/invites")
async def invite_member(
    invite_data: TeamInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Приглашение нового участника в команду"""
    if not current_user.team:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в команде")
    
    if not current_user.is_captain:
        raise HTTPException(status_code=403, detail="Только капитан может приглашать участников")
    
    invitation_service = InvitationService(db)
    email_service = EmailService()
    
    # Проверка максимального количества участников
    if len(current_user.team.members) >= 5:
        raise HTTPException(status_code=400, detail="Команда уже достигла максимального размера")
    
    # Создание приглашения
    invitation = invitation_service.create_invitation(
        team_id=current_user.team.id,
        email=invite_data.email,
        invited_by_id=current_user.id
    )
    
    # Отправка email с приглашением
    await email_service.send_invitation_email(
        email=invite_data.email,
        team_name=current_user.team.name,
        inviter_name=current_user.username
    )
    
    return {"message": "Приглашение отправлено"}

@router.get("/invites")
async def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка pending приглашений команды"""
    if not current_user.team or not current_user.is_captain:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    invitations = db.query(Invitation).filter(
        Invitation.team_id == current_user.team.id,
        Invitation.status == "pending"
    ).all()
    
    return [
        {
            "id": inv.id,
            "email": inv.email,
            "created_at": inv.created_at,
            "expires_at": inv.expires_at
        }
        for inv in invitations
    ]
