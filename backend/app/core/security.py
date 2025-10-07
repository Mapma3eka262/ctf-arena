from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

# Контекст для хеширования паролей с исправлением для Python 3.12
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    # Fallback на прямую работу с bcrypt если passlib не работает
    import bcrypt
    pwd_context = None
    print(f"⚠️  Passlib bcrypt context failed, using direct bcrypt: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    if pwd_context:
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Прямая проверка с bcrypt
        import bcrypt
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    if pwd_context:
        return pwd_context.hash(password)
    else:
        # Прямое хеширование с bcrypt
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Union[str, None]:
    """Верификация JWT токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def validate_flag_format(flag: str) -> bool:
    """Проверка формата флага"""
    return flag.startswith("CTF{") and flag.endswith("}") and len(flag) > 6

def sanitize_input(input_string: str) -> str:
    """Очистка пользовательского ввода"""
    import html
    return html.escape(input_string.strip())
