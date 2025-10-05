import logging
from telegram import Bot
from telegram.error import TelegramError
from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    _bot = None
    
    @classmethod
    def get_bot(cls):
        """Получение экземпляра бота"""
        if cls._bot is None and settings.TELEGRAM_BOT_TOKEN:
            cls._bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        return cls._bot
    
    @classmethod
    def send_message(cls, chat_id: str, message: str) -> bool:
        """Отправка сообщения в Telegram"""
        try:
            bot = cls.get_bot()
            if not bot:
                logger.warning("Telegram bot not configured")
                return False
            
            bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Telegram message sent to {chat_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram message sending failed: {e}")
            return False
    
    @classmethod
    def send_admin_alert(cls, message: str) -> bool:
        """Отправка уведомления администраторам"""
        if not settings.TELEGRAM_ADMIN_CHAT_ID:
            logger.warning("Telegram admin chat ID not configured")
            return False
        
        return cls.send_message(settings.TELEGRAM_ADMIN_CHAT_ID, f"🚨 {message}")
    
    @classmethod
    def send_service_status_alert(cls, service_name: str, status: str):
        """Уведомление о изменении статуса сервиса"""
        message = f"Сервис {service_name} изменил статус: {status}"
        return cls.send_admin_alert(message)
    
    @classmethod
    def send_first_blood_alert(cls, challenge_name: str, team_name: str, user_name: str):
        """Уведомление о первой крови"""
        message = f"🎉 Первая кровь! {user_name} из команды {team_name} решил задание {challenge_name}"
        return cls.send_admin_alert(message)