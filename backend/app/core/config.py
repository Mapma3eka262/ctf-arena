# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any

class Settings(BaseSettings):
    """Расширенные настройки приложения"""
    
    # Настройки приложения
    APP_NAME: str = "CyberCTF Arena"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Настройки базы данных
    DATABASE_URL: str = "postgresql://ctfuser:ctfpassword@localhost/ctfarena"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Настройки JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа
    
    # Настройки CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Настройки email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Настройки Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Настройки Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Настройки файлов
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Настройки соревнования
    COMPETITION_START_TIME: str = "2024-09-25T00:00:00"
    COMPETITION_END_TIME: str = "2024-09-27T23:59:59"
    MAX_TEAM_SIZE: int = 5
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/opt/ctf-arena/logs/ctf-arena.log"
    
    # Настройки WebSocket
    WEBSOCKET_HOST: str = "0.0.0.0"
    WEBSOCKET_PORT: int = 8001
    
    # Настройки безопасности
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    ENABLE_AUDIT_LOG: bool = True
    
    # Настройки динамических заданий
    DOCKER_NETWORK: str = "ctf_network"
    MAX_CONCURRENT_INSTANCES: int = 50
    INSTANCE_TIMEOUT: int = 3600  # 1 hour
    
    # Настройки плагинов
    PLUGINS_ENABLED: bool = True
    PLUGINS_DIR: str = "app/plugins"
    
    # Мониторинг
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    class Config:
        env_file = "/opt/ctf-arena/.env"
        case_sensitive = False

settings = Settings()