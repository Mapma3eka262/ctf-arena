from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ctf_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.monitoring_tasks", 
        "app.tasks.invitation_tasks",
        "app.tasks.cleanup_tasks"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    task_routes={
        'app.tasks.email_tasks.*': {'queue': 'email'},
        'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
        'app.tasks.invitation_tasks.*': {'queue': 'default'},
        'app.tasks.cleanup_tasks.*': {'queue': 'cleanup'},
    }
)