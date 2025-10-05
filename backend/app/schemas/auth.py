from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class RegisterRequest(BaseModel):
    team_name: str
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    role: Optional[str] = None

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

class EmailVerificationRequest(BaseModel):
    token: str