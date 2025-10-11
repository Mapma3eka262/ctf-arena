# backend/celery_config.py
from app.core.config import settings

# Конфигурация Celery для Ubuntu
broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL

# Настройки для Ubuntu production
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Moscow'
enable_utc = True

# Оптимизации для production
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000
task_acks_late = True
worker_disable_rate_limits = False

# Очереди
task_routes = {
    'app.tasks.email_tasks.*': {'queue': 'email'},
    'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
    'app.tasks.invitation_tasks.*': {'queue': 'default'},
    'app.tasks.cleanup_tasks.*': {'queue': 'cleanup'},
}

# Расписание задач для Ubuntu
beat_schedule = {
    'check-services-every-5-minutes': {
        'task': 'app.tasks.monitoring_tasks.check_all_services_task',
        'schedule': 300.0,  # 5 минут
    },
    'cleanup-expired-invitations-daily': {
        'task': 'app.tasks.invitation_tasks.cleanup_expired_invitations_task',
        'schedule': 86400.0,  # 24 часа
    },
    'cleanup-old-submissions-weekly': {
        'task': 'app.tasks.cleanup_tasks.cleanup_old_submissions_task',
        'schedule': 604800.0,  # 7 дней
    },
    'rotate-flags-daily': {
        'task': 'app.tasks.cleanup_tasks.rotate_flags_task',
        'schedule': 86400.0,  # 24 часа
    },
    'backup-database-daily': {
        'task': 'app.tasks.cleanup_tasks.backup_database_task',
        'schedule': 86400.0,  # 24 часа
    },
    'cleanup-inactive-users-monthly': {
        'task': 'app.tasks.cleanup_tasks.cleanup_inactive_users_task',
        'schedule': 2592000.0,  # 30 дней
    },
}