from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from fastapi import HTTPException

from app.models import TeamInvite, User, Team
from app.core.config import settings
from app.tasks.email_tasks import send_team_invitation

class InvitationService:
    
    @staticmethod
    def create_invitation(db: Session, team_id: int, invited_by: int, email: str) -> dict:
        """Создание приглашения в команду"""
        # Проверка существования пользователя с таким email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user and existing_user.team_id:
            raise HTTPException(status_code=400, detail="User already in a team")
        
        # Проверка существования приглашения
        existing_invite = db.query(TeamInvite).filter(
            TeamInvite.team_id == team_id,
            TeamInvite.email == email,
            TeamInvite.status == 'pending'
        ).first()
        
        if existing_invite:
            raise HTTPException(status_code=400, detail="Invitation already sent")
        
        # Проверка размера команды
        team = db.query(Team).filter(Team.id == team_id).first()
        if team and len(team.members) >= settings.MAX_TEAM_SIZE:
            raise HTTPException(status_code=400, detail="Team is full")
        
        # Создание приглашения
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)
        
        invite = TeamInvite(
            team_id=team_id,
            email=email,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at,
            status='pending'
        )
        
        db.add(invite)
        db.commit()
        
        # Отправка email приглашения
        send_team_invitation.delay(invite.id)
        
        return {
            "id": invite.id,
            "email": invite.email,
            "status": invite.status,
            "expires_at": invite.expires_at,
            "invited_by": invite.inviter.username
        }
    
    @staticmethod
    def accept_invitation(db: Session, token: str, user_id: int) -> dict:
        """Принятие приглашения"""
        invite = db.query(TeamInvite).filter(TeamInvite.token == token).first()
        if not invite:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        # Проверка срока действия
        if datetime.utcnow() > invite.expires_at:
            invite.status = 'expired'
            db.commit()
            raise HTTPException(status_code=400, detail="Invitation expired")
        
        # Проверка статуса
        if invite.status != 'pending':
            raise HTTPException(status_code=400, detail="Invitation already processed")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверка email
        if user.email != invite.email:
            raise HTTPException(status_code=400, detail="Email does not match invitation")
        
        # Проверка, что пользователь не в другой команде
        if user.team_id:
            raise HTTPException(status_code=400, detail="User already in a team")
        
        # Проверка размера команды
        team = invite.team
        if len(team.members) >= settings.MAX_TEAM_SIZE:
            raise HTTPException(status_code=400, detail="Team is full")
        
        # Добавление пользователя в команду
        user.team_id = team.id
        user.role = 'member'
        
        # Обновление статуса приглашения
        invite.status = 'accepted'
        
        db.commit()
        
        return {"message": "Invitation accepted successfully"}
    
    @staticmethod
    def cleanup_expired_invitations(db: Session):
        """Очистка просроченных приглашений"""
        expired_invites = db.query(TeamInvite).filter(
            TeamInvite.status == 'pending',
            TeamInvite.expires_at < datetime.utcnow()
        ).all()
        
        for invite in expired_invites:
            invite.status = 'expired'
        
        db.commit()
        return len(expired_invites)