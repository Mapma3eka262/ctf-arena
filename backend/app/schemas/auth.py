from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    team_name: str

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Логин должен содержать минимум 3 символа')
        if not v.isalnum():
            raise ValueError('Логин должен содержать только буквы и цифры')
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v

class Token(BaseModel):
    """Схема для JWT токена"""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """Данные из JWT токена"""
    username: Optional[str] = None