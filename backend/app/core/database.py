# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Генератор сессий базы данных для Dependency Injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Инициализация базы данных - создание таблиц"""
    try:
        # Импортируем все модели здесь, чтобы они были зарегистрированы в Base.metadata
        from app.models.user import User
        from app.models.team import Team
        from app.models.challenge import Challenge
        from app.models.submission import Submission
        from app.models.service import Service
        from app.models.invitation import Invitation
        from app.models.competition import Competition
        from app.models.dynamic_challenge import DynamicChallenge, ChallengeInstance
        from app.models.notification import Notification
        from app.models.audit_log import AuditLog
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы базы данных созданы успешно")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

def check_db_connection():
    """Проверка подключения к базе данных"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False