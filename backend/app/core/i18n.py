from typing import Dict
from app.core.config import settings

# Локализованные сообщения
MESSAGES = {
    "ru": {
        "welcome": "Добро пожаловать в CyberCTF Arena",
        "registration_success": "Регистрация успешно завершена",
        "invalid_credentials": "Неверные учетные данные",
        "email_verification_required": "Требуется подтверждение email",
        "team_not_found": "Команда не найдена",
        "challenge_not_found": "Задание не найдено",
        "flag_accepted": "Флаг принят",
        "flag_rejected": "Неверный флаг",
        "first_blood": "Первая кровь!",
        "service_online": "Сервис онлайн",
        "service_offline": "Сервис офлайн",
        "invitation_sent": "Приглашение отправлено",
        "invitation_accepted": "Приглашение принято",
        "invitation_expired": "Приглашение просрочено",
        "access_denied": "Доступ запрещен",
        "validation_error": "Ошибка валидации данных"
    },
    "en": {
        "welcome": "Welcome to CyberCTF Arena",
        "registration_success": "Registration completed successfully",
        "invalid_credentials": "Invalid credentials",
        "email_verification_required": "Email verification required",
        "team_not_found": "Team not found",
        "challenge_not_found": "Challenge not found",
        "flag_accepted": "Flag accepted",
        "flag_rejected": "Invalid flag",
        "first_blood": "First blood!",
        "service_online": "Service online",
        "service_offline": "Service offline",
        "invitation_sent": "Invitation sent",
        "invitation_accepted": "Invitation accepted",
        "invitation_expired": "Invitation expired",
        "access_denied": "Access denied",
        "validation_error": "Data validation error"
    }
}

def get_message(key: str, language: str = None) -> str:
    """Получение локализованного сообщения"""
    lang = language or settings.DEFAULT_LANGUAGE
    return MESSAGES.get(lang, {}).get(key, key)

class Translator:
    def __init__(self, language: str = None):
        self.language = language or settings.DEFAULT_LANGUAGE
    
    def translate(self, key: str) -> str:
        return get_message(key, self.language)