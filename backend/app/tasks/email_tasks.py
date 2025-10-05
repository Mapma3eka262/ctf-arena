from celery import shared_task
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
from sqlalchemy.orm import Session

from app.tasks.celery import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(user_id: int, verification_token: str):
    """Отправка email для верификации"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for email verification")
            return
        
        subject = "Подтверждение email - CyberCTF Arena"
        body = f"""
        Здравствуйте, {user.username}!
        
        Для завершения регистрации в CyberCTF Arena подтвердите ваш email.
        
        Код подтверждения: {verification_token}
        
        Или перейдите по ссылке:
        {settings.FRONTEND_URL}/verify-email?token={verification_token}
        
        Если вы не регистрировались в системе, проигнорируйте это письмо.
        """
        
        send_email(user.email, subject, body)
        logger.info(f"Verification email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
    finally:
        db.close()

@shared_task
def send_password_reset_email(user_id: int, reset_token: str):
    """Отправка email для сброса пароля"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for password reset")
            return
        
        subject = "Сброс пароля - CyberCTF Arena"
        body = f"""
        Здравствуйте, {user.username}!
        
        Для сброса пароля перейдите по ссылке:
        {settings.FRONTEND_URL}/reset-password?token={reset_token}
        
        Ссылка действительна в течение 1 часа.
        
        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
        """
        
        send_email(user.email, subject, body)
        logger.info(f"Password reset email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
    finally:
        db.close()

@shared_task
def send_team_invitation(invite_id: int):
    """Отправка приглашения в команду"""
    try:
        db = next(get_db())
        invite = db.query(TeamInvite).filter(TeamInvite.id == invite_id).first()
        if not invite:
            logger.error(f"Invite {invite_id} not found")
            return
        
        team = invite.team
        invited_by = db.query(User).filter(User.id == invite.invited_by).first()
        
        subject = f"Приглашение в команду {team.name} - CyberCTF Arena"
        body = f"""
        Здравствуйте!
        
        Вы получили приглашение присоединиться к команде "{team.name}" от {invited_by.username}.
        
        Для принятия приглашения перейдите по ссылке:
        {settings.FRONTEND_URL}/accept-invite?token={invite.token}
        
        Ссылка действительна в течение 24 часов.
        """
        
        send_email(invite.email, subject, body)
        logger.info(f"Team invitation sent to {invite.email}")
        
    except Exception as e:
        logger.error(f"Failed to send team invitation: {e}")
    finally:
        db.close()

@shared_task
def send_submission_result(submission_id: int):
    """Отправка результата проверки флага"""
    try:
        db = next(get_db())
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error(f"Submission {submission_id} not found")
            return
        
        user = submission.user
        challenge = submission.challenge
        
        subject = "Результат проверки флага - CyberCTF Arena"
        
        if submission.status == 'accepted':
            body = f"""
            Поздравляем, {user.username}!
            
            Ваш флаг для задания "{challenge.title}" принят!
            
            Начислено очков: {submission.points_awarded}
            {"🎉 Первая кровь! 🎉" if submission.is_first_blood else ""}
            
            Текущий счет команды: {submission.team.score}
            """
        else:
            body = f"""
            {user.username}, ваш флаг для задания "{challenge.title}" отклонен.
            
            Попробуйте еще раз!
            """
        
        send_email(user.email, subject, body)
        logger.info(f"Submission result email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send submission result: {e}")
    finally:
        db.close()

def send_email(to_email: str, subject: str, body: str):
    """Базовая функция отправки email"""
    try:
        if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
            logger.warning("Email configuration missing, skipping email send")
            return
        
        message = MimeMultipart()
        message['From'] = settings.FROM_EMAIL
        message['To'] = to_email
        message['Subject'] = subject
        
        message.attach(MimeText(body, 'plain'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
            
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise