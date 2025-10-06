import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD

    async def send_confirmation_email(self, email: str, username: str):
        """Отправка email подтверждения регистрации"""
        subject = "Подтверждение регистрации в CyberCTF Arena"
        body = f"""
        Здравствуйте, {username}!
        
        Благодарим за регистрацию в CyberCTF Arena.
        Ваш аккаунт успешно создан и активирован.
        
        Присоединяйтесь к соревнованиям и покажите свои навыки!
        
        С уважением,
        Команда CyberCTF Arena
        """
        
        await self._send_email(email, subject, body)

    async def send_invitation_email(self, email: str, team_name: str, inviter_name: str):
        """Отправка email с приглашением в команду"""
        subject = f"Приглашение в команду {team_name}"
        body = f"""
        Здравствуйте!
        
        {inviter_name} приглашает вас присоединиться к команде "{team_name}" в CyberCTF Arena.
        
        Для принятия приглашения войдите в систему и перейдите в раздел "Приглашения".
        
        С уважением,
        Команда CyberCTF Arena
        """
        
        await self._send_email(email, subject, body)

    async def send_password_reset_email(self, email: str, reset_token: str):
        """Отправка email для сброса пароля"""
        subject = "Сброс пароля CyberCTF Arena"
        body = f"""
        Вы запросили сброс пароля для вашего аккаунта в CyberCTF Arena.
        
        Для сброса пароля используйте следующий токен:
        {reset_token}
        
        Если вы не запрашивали сброс пароля, проигнорируйте это сообщение.
        
        С уважением,
        Команда CyberCTF Arena
        """
        
        await self._send_email(email, subject, body)

    async def _send_email(self, to_email: str, subject: str, body: str):
        """Базовая функция отправки email"""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            print(f"Email не отправлен (не настроен SMTP): {to_email} - {subject}")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email отправлен: {to_email}")
        except Exception as e:
            print(f"Ошибка отправки email: {e}")