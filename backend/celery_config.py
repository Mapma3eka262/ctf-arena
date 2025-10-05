from app.core.config import settings

# Конфигурация Celery
broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Moscow'
enable_utc = True

# Расписание задач
beat_schedule = {
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