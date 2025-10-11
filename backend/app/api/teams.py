# backend/app/api/teams.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.team import TeamResponse, TeamUpdate, TeamInvite
from app.schemas.user import UserResponse  # ДОБАВЬТЕ ЭТУ СТРОКУ
from app.schemas.invitation import InvitationResponse
from app.models.team import Team
from app.models.user import User
from app.services.invitation_service import InvitationService
from app.services.audit_service import AuditService
from app.tasks.email_tasks import send_invitation_email_task

router = APIRouter()

@router.get("/my", response_model=TeamResponse)
async def get_my_team(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о команде текущего пользователя"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    
    # Формирование информации о участниках
    members = []
    for member in team.members:
        members.append({
            "id": member.id,
            "username": member.username,
            "email": member.email,
            "role": "captain" if member.is_captain else "member",
            "is_active": member.is_active,
            "joined_at": member.joined_at
        })
    
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "score": team.score,
        "country": team.country,
        "website": team.website,
        "created_at": team.created_at,
        "members": members
    }

@router.put("/my", response_model=TeamResponse)
async def update_my_team(
    team_update: TeamUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о команде"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    if not current_user.is_captain:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только капитан может изменять информацию о команде"
        )
    
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    
    # Обновление полей
    update_data = team_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)
    
    db.commit()
    db.refresh(team)
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="team_update",
        resource_type="team",
        user_id=current_user.id,
        resource_id=team.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return await get_my_team(current_user, db)

@router.post("/invites", response_model=InvitationResponse)
async def invite_to_team(
    invite_data: TeamInvite,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Приглашение пользователя в команду"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    if not current_user.is_captain:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только капитан может приглашать участников"
        )
    
    # Проверка максимального размера команды
    if len(current_user.team.members) >= 5:  # MAX_TEAM_SIZE
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Команда достигла максимального размера"
        )
    
    invitation_service = InvitationService(db)
    
    # Создание приглашения
    invitation = invitation_service.create_invitation(
        team_id=current_user.team_id,
        email=invite_data.email,
        invited_by_id=current_user.id
    )
    
    # Отправка email приглашения
    send_invitation_email_task.delay(
        invite_data.email,
        current_user.team.name,
        current_user.username
    )
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="team_invitation_sent",
        resource_type="team",
        user_id=current_user.id,
        resource_id=current_user.team_id,
        details={"invited_email": invite_data.email}
    )
    
    return invitation

@router.get("/invites", response_model=List[InvitationResponse])
async def get_team_invites(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка приглашений команды"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    if not current_user.is_captain:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только капитан может просматривать приглашения"
        )
    
    from app.models.invitation import Invitation
    invitations = db.query(Invitation).filter(
        Invitation.team_id == current_user.team_id
    ).all()
    
    return invitations

@router.post("/invites/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принятие приглашения в команду"""
    from app.models.invitation import Invitation
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Приглашение не найдено"
        )
    
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это приглашение предназначено другому пользователю"
        )
    
    if current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже состоите в команде"
        )
    
    invitation_service = InvitationService(db)
    success = invitation_service.accept_invitation(invitation.token, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось принять приглашение"
        )
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="team_invitation_accepted",
        resource_type="team",
        user_id=current_user.id,
        resource_id=invitation.team_id,
        details={"invitation_id": invitation_id}
    )
    
    return {"message": "Приглашение принято"}

@router.get("/leaderboard")
async def get_leaderboard(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получение таблицы лидеров"""
    teams = db.query(Team).order_by(Team.score.desc()).offset(skip).limit(limit).all()
    
    leaderboard = []
    for index, team in enumerate(teams, start=1):
        leaderboard.append({
            "position": index + skip,
            "id": team.id,
            "name": team.name,
            "score": team.score,
            "country": team.country,
            "member_count": len(team.members)
        })
    
    return {
        "leaderboard": leaderboard,
        "total": db.query(Team).count()
    }
