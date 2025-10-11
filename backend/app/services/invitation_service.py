# backend/app/services/invitation_service.py
import secrets
import string
from sqlalchemy.orm import Session
from app.models.invitation import Invitation
from app.models.user import User

class InvitationService:
    def __init__(self, db: Session):
        self.db = db

    def create_invitation(self, team_id: int, email: str, invited_by_id: int) -> Invitation:
        """Создание приглашения в команду"""
        # Генерация токена
        token = self._generate_token()
        
        invitation = Invitation(
            team_id=team_id,
            email=email,
            invited_by_id=invited_by_id,
            token=token
        )
        
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        
        return invitation

    def accept_invitation(self, token: str, user_id: int) -> bool:
        """Принятие приглашения"""
        invitation = self.db.query(Invitation).filter(
            Invitation.token == token,
            Invitation.status == "pending"
        ).first()
        
        if not invitation or invitation.is_expired():
            return False

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Проверяем, не состоит ли пользователь уже в команде
        if user.team_id:
            return False

        # Добавляем пользователя в команду
        user.team_id = invitation.team_id
        invitation.status = "accepted"
        
        self.db.commit()
        return True

    def _generate_token(self, length: int = 32) -> str:
        """Генерация случайного токена"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def cleanup_expired_invitations(self):
        """Очистка просроченных приглашений"""
        from datetime import datetime
        
        expired_invitations = self.db.query(Invitation).filter(
            Invitation.status == "pending",
            Invitation.expires_at < datetime.utcnow()
        ).all()
        
        for invitation in expired_invitations:
            invitation.status = "expired"
        
        self.db.commit()
        return len(expired_invitations)