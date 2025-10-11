# backend/app/core/i18n.py
"""
Модуль интернационализации (i18n) для CyberCTF Arena
Пока реализована базовая структура для будущей поддержки мультиязычности
"""

from typing import Dict, Any

# Базовые переводы (русский язык по умолчанию)
TRANSLATIONS = {
    "ru": {
        # Общие фразы
        "welcome": "Добро пожаловать в CyberCTF Arena",
        "error": "Ошибка",
        "success": "Успех",
        "warning": "Предупреждение",
        "info": "Информация",
        
        # Аутентификация
        "login_success": "Вход выполнен успешно",
        "login_failed": "Неверный логин или пароль",
        "registration_success": "Регистрация завершена успешно",
        "logout_success": "Выход выполнен успешно",
        
        # Задания
        "challenge_solved": "Задание решено!",
        "flag_accepted": "Флаг принят",
        "flag_rejected": "Неверный флаг",
        "already_solved": "Вы уже решили это задание",
        
        # Команды
        "team_created": "Команда создана",
        "invitation_sent": "Приглашение отправлено",
        "invitation_accepted": "Приглашение принято",
        
        # Ошибки
        "not_authenticated": "Требуется аутентификация",
        "permission_denied": "Недостаточно прав",
        "not_found": "Ресурс не найден",
        "rate_limited": "Слишком много запросов",
        
        # Валидация
        "invalid_email": "Неверный формат email",
        "invalid_username": "Неверный формат имени пользователя",
        "weak_password": "Слишком слабый пароль",
        "passwords_mismatch": "Пароли не совпадают",
        
        # Уведомления
        "first_blood": "Первая кровь!",
        "new_solve": "Новое решение задания",
        "service_down": "Сервис недоступен",
        "competition_started": "Соревнование началось",
        "competition_ended": "Соревнование завершено"
    },
    "en": {
        # English translations can be added here
        "welcome": "Welcome to CyberCTF Arena",
        "error": "Error",
        "success": "Success",
        # ... other translations
    }
}

class Translator:
    """Класс для управления переводами"""
    
    def __init__(self, default_language: str = "ru"):
        self.default_language = default_language
        self.current_language = default_language
    
    def set_language(self, language: str):
        """Установка текущего языка"""
        if language in TRANSLATIONS:
            self.current_language = language
        else:
            self.current_language = self.default_language
    
    def get(self, key: str, language: str = None, **kwargs) -> str:
        """Получение перевода по ключу"""
        lang = language or self.current_language
        
        # Получаем перевод или используем ключ как значение по умолчанию
        translation = TRANSLATIONS.get(lang, {}).get(key, key)
        
        # Заменяем плейсхолдеры если есть
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def get_available_languages(self) -> list:
        """Получение списка доступных языков"""
        return list(TRANSLATIONS.keys())

# Глобальный экземпляр переводчика
translator = Translator()

# Удобные функции для быстрого доступа
def t(key: str, **kwargs) -> str:
    """Быстрый доступ к переводу"""
    return translator.get(key, **kwargs)

def set_language(language: str):
    """Установка языка"""
    translator.set_language(language)

def get_available_languages() -> list:
    """Получение доступных языков"""
    return translator.get_available_languages()

# Middleware для определения языка из заголовков запроса
def get_request_language(request) -> str:
    """Определение языка из заголовков HTTP запроса"""
    accept_language = request.headers.get("accept-language", "")
    
    # Парсим заголовок Accept-Language
    languages = accept_language.split(",")
    for lang in languages:
        lang_code = lang.split(";")[0].strip().split("-")[0].lower()
        if lang_code in TRANSLATIONS:
            return lang_code
    
    return translator.default_language