from typing import Dict

# Локализованные сообщения
MESSAGES = {
    "ru": {
        "welcome": "Добро пожаловать в CyberCTF Arena",
        "registration_success": "Регистрация успешна",
        "invalid_credentials": "Неверный логин или пароль",
        "team_full": "Команда уже достигла максимального размера",
        "flag_correct": "Флаг верный!",
        "flag_incorrect": "Неверный флаг",
        "challenge_solved": "Задание уже решено",
        "permission_denied": "Доступ запрещен",
    },
    "en": {
        "welcome": "Welcome to CyberCTF Arena",
        "registration_success": "Registration successful",
        "invalid_credentials": "Invalid username or password",
        "team_full": "Team has reached maximum size",
        "flag_correct": "Flag is correct!",
        "flag_incorrect": "Incorrect flag",
        "challenge_solved": "Challenge already solved",
        "permission_denied": "Permission denied",
    }
}

def get_message(key: str, lang: str = "ru") -> str:
    """Получение локализованного сообщения"""
    return MESSAGES.get(lang, {}).get(key, key)