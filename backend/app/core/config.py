from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "postgresql://user:password@localhost/cyberctf"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@cyberctf.ru"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_CHAT_ID: str = ""
    
    # Приложение
    FRONTEND_URL: str = "http://localhost:3000"
    INVITATION_EXPIRE_HOURS: int = 24
    
    # Мониторинг
    SERVICE_CHECK_TIMEOUT: int = 10
    DEFAULT_CHECK_INTERVAL: int = 3  # минуты
    
    # Соревнование
    DEFAULT_PENALTY_MINUTES: int = 30
    MAX_TEAM_SIZE: int = 5
    
    # Языки
    SUPPORTED_LANGUAGES: List[str] = ["ru", "en"]
    DEFAULT_LANGUAGE: str = "ru"
    
    class Config:
        env_file = ".env"

settings = Settings()