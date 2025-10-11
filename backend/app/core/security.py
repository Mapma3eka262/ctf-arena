# backend/app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import re
from app.core.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def validate_flag_format(flag: str) -> bool:
    """
    Валидация формата флага
    Стандартный формат: CTF{...}
    """
    if not flag.startswith("CTF{"):
        return False
    
    if not flag.endswith("}"):
        return False
    
    if len(flag) < 7:  # CTF{} + минимум 1 символ внутри
        return False
    
    # Проверяем, что внутри есть хотя бы один символ
    flag_content = flag[4:-1]
    if not flag_content.strip():
        return False
    
    return True

def decode_token(token: str) -> Optional[dict]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def validate_username(username: str) -> bool:
    """Валидация имени пользователя"""
    if len(username) < 3 or len(username) > 50:
        return False
    
    # Только буквы, цифры и подчеркивания
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    # Должен начинаться с буквы
    if not re.match(r'^[a-zA-Z]', username):
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> bool:
    """Проверка сложности пароля"""
    if len(password) < 6:
        return False
    
    # Проверка на наличие цифр
    if not any(char.isdigit() for char in password):
        return False
    
    # Проверка на наличие букв в верхнем регистре
    if not any(char.isupper() for char in password):
        return False
    
    # Проверка на наличие букв в нижнем регистре
    if not any(char.islower() for char in password):
        return False
    
    return True

def generate_secure_flag() -> str:
    """Генерация безопасного флага"""
    import secrets
    import string
    
    # Генерация случайной строки длиной 16 символов
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    return f"CTF{{{random_part}}}"

def sanitize_input(input_string: str) -> str:
    """Очистка пользовательского ввода от потенциально опасных символов"""
    import html
    
    # Экранирование HTML символов
    sanitized = html.escape(input_string)
    
    # Удаление потенциально опасных последовательностей
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+='  # onload, onclick и т.д.
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()