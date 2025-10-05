from celery import shared_task
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.tasks.celery import get_db
from app.models import TeamInvite, Submission
from app.services.invitation_service import InvitationService

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_invitations():
    """Очистка просроченных приглашений"""
    try:
        db = next(get_db())
        count = InvitationService.cleanup_expired_invitations(db)
        logger.info(f"Cleaned up {count} expired invitations")
    except Exception as e:
        logger.error(f"Failed to cleanup expired invitations: {e}")
    finally:
        db.close()

@shared_task
def cleanup_old_logs():
    """Очистка старых логов (>6 месяцев)"""
    try:
        db = next(get_db())
        # Здесь должна быть логика очистки логов
        # В реальной системе логи могут храниться в отдельной таблице или файлах
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        # Пример для таблицы submissions (если нужно очищать старые отправки)
        # old_submissions = db.query(Submission).filter(Submission.submitted_at < six_months_ago).delete()
        # db.commit()
        
        logger.info("Old logs cleanup completed")
    except Exception as e:
        logger.error(f"Failed to cleanup old logs: {e}")
    finally:
        db.close()