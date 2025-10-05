from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base

# Создание Celery приложения
celery_app = Celery(
    'cyberctf',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.email_tasks',
        'app.tasks.monitoring_tasks',
        'app.tasks.invitation_tasks',
        'app.tasks.cleanup_tasks'
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    beat_schedule={
        'monitor-services-every-3-minutes': {
            'task': 'app.tasks.monitoring_tasks.monitor_all_services',
            'schedule': 180.0,  # 3 минуты
        },
        'cleanup-expired-invitations': {
            'task': 'app.tasks.cleanup_tasks.cleanup_expired_invitations',
            'schedule': 3600.0,  # 1 час
        },
        'check-competition-time': {
            'task': 'app.tasks.monitoring_tasks.check_competition_time',
            'schedule': 60.0,  # 1 минута
        },
    }
)

# Создание сессии БД для задач
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()