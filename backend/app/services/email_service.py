import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
        """Отправка email"""
        try:
            if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
                logger.warning("Email configuration missing, skipping email send")
                return False
            
            message = MimeMultipart()
            message['From'] = settings.FROM_EMAIL
            message['To'] = to_email
            message['Subject'] = subject
            
            if is_html:
                message.attach(MimeText(body, 'html'))
            else:
                message.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    @staticmethod
    def send_verification_email(email: str, username: str, verification_token: str):
        """Отправка email для верификации"""
        subject = "Подтверждение email - CyberCTF Arena"
        body = f"""
        Здравствуйте, {username}!
        
        Для завершения регистрации в CyberCTF Arena подтвердите ваш email.
        
        Код подтверждения: {verification_token}
        
        Или перейдите по ссылке:
        {settings.FRONTEND_URL}/verify-email?token={verification_token}
        
        Если вы не регистрировались в системе, проигнорируйте это письмо.
        """
        
        return EmailService.send_email(email, subject, body)
    
    @staticmethod
    def send_password_reset_email(email: str, username: str, reset_token: str):
        """Отправка email для сброса пароля"""
        subject = "Сброс пароля - CyberCTF Arena"
        body = f"""
        Здравствуйте, {username}!
        
        Для сброса пароля перейдите по ссылке:
        {settings.FRONTEND_URL}/reset-password?token={reset_token}
        
        Ссылка действительна в течение 1 часа.
        
        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
        """
        
        return EmailService.send_email(email, subject, body)
    
    @staticmethod
    def send_team_invitation_email(email: str, team_name: str, inviter_name: str, invite_token: str):
        """Отправка приглашения в команду"""
        subject = f"Приглашение в команду {team_name} - CyberCTF Arena"
        body = f"""
        Здравствуйте!
        
        Вы получили приглашение присоединиться к команде "{team_name}" от {inviter_name}.
        
        Для принятия приглашения перейдите по ссылке:
        {settings.FRONTEND_URL}/accept-invite?token={invite_token}
        
        Ссылка действительна в течение 24 часов.
        """
        
        return EmailService.send_email(email, subject, body)