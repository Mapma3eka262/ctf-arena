from celery import shared_task
import logging
from sqlalchemy.orm import Session

from app.tasks.celery import get_db
from app.models import TeamInvite, User, Team
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

@shared_task
def send_team_invitation(invite_id: int):
    """Отправка приглашения в команду по email"""
    try:
        db = next(get_db())
        invite = db.query(TeamInvite).filter(TeamInvite.id == invite_id).first()
        if not invite:
            logger.error(f"Invite {invite_id} not found")
            return
        
        team = invite.team
        invited_by = db.query(User).filter(User.id == invite.invited_by).first()
        
        EmailService.send_team_invitation_email(
            email=invite.email,
            team_name=team.name,
            inviter_name=invited_by.username,
            invite_token=invite.token
        )
        
        logger.info(f"Team invitation sent to {invite.email}")
        
    except Exception as e:
        logger.error(f"Failed to send team invitation: {e}")
    finally:
        db.close()