import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Валидация имени пользователя
    Возвращает (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Логин должен содержать минимум 3 символа"
    
    if len(username) > 50:
        return False, "Логин не должен превышать 50 символов"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Логин может содержать только буквы, цифры и подчеркивания"
    
    if not re.match(r'^[a-zA-Z]', username):
        return False, "Логин должен начинаться с буквы"
    
    return True, None

def validate_email_address(email: str) -> tuple[bool, Optional[str]]:
    """
    Валидация email адреса
    """
    try:
        validate_email(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Валидация пароля
    """
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    
    if len(password) > 100:
        return False, "Пароль не должен превышать 100 символов"
    
    # Проверка на сложность (опционально)
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    
    return True, None

def validate_team_name(team_name: str) -> tuple[bool, Optional[str]]:
    """
    Валидация названия команды
    """
    if len(team_name) < 2:
        return False, "Название команды должно содержать минимум 2 символа"
    
    if len(team_name) > 100:
        return False, "Название команды не должно превышать 100 символов"
    
    if not re.match(r'^[a-zA-Z0-9а-яА-ЯёЁ _-]+$', team_name):
        return False, "Название команды содержит недопустимые символы"
    
    return True, None

def validate_flag_format(flag: str) -> tuple[bool, Optional[str]]:
    """
    Валидация формата флага
    """
    if not flag.startswith("CTF{"):
        return False, "Флаг должен начинаться с CTF{"
    
    if not flag.endswith("}"):
        return False, "Флаг должен заканчиваться }"
    
    if len(flag) < 7:  # CTF{} + минимум 1 символ
        return False, "Флаг слишком короткий"
    
    if len(flag) > 500:
        return False, "Флаг слишком длинный"
    
    flag_content = flag[4:-1]  # Извлекаем содержимое между CTF{ и }
    if not flag_content.strip():
        return False, "Флаг не может быть пустым"
    
    return True, None

def validate_challenge_points(points: int) -> tuple[bool, Optional[str]]:
    """
    Валидация количества очков за задание
    """
    if points < 0:
        return False, "Очки не могут быть отрицательными"
    
    if points > 1000:
        return False, "Слишком большое количество очков"
    
    return True, None