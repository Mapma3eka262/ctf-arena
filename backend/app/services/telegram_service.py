import requests
from app.core.config import settings

class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def send_notification(self, message: str):
        """Отправка уведомления в Telegram"""
        if not self.bot_token or not self.chat_id:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки Telegram уведомления: {e}")
            return False

    async def send_flag_submission_notification(self, username: str, challenge_title: str, status: str):
        """Уведомление об отправке флага"""
        message = f"""
🚩 <b>Новая отправка флага</b>

👤 Пользователь: {username}
🎯 Задание: {challenge_title}
📊 Статус: {status}
        """
        await self.send_notification(message)

    async def send_first_blood_notification(self, username: str, challenge_title: str, team_name: str):
        """Уведомление о First Blood"""
        message = f"""
🩸 <b>First Blood!</b>

👤 Игрок: {username}
🏴‍☠️ Команда: {team_name}
🎯 Задание: {challenge_title}

Поздравляем с первой кровью! 🎉
        """
        await self.send_notification(message)