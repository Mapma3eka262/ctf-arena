# backend/app/tasks/__init__.py
from app.tasks.celery import celery_app
from app.tasks.email_tasks import (
    send_confirmation_email_task,
    send_invitation_email_task,
    send_password_reset_email_task,
    send_notification_to_all_users_task
)
from app.tasks.monitoring_tasks import (
    check_all_services_task,
    update_service_metrics_task
)
from app.tasks.invitation_tasks import (
    cleanup_expired_invitations_task,
    send_invitation_reminder_task
)
from app.tasks.cleanup_tasks import (
    cleanup_old_submissions_task,
    cleanup_inactive_users_task,
    rotate_flags_task,
    backup_database_task
)

__all__ = [
    'celery_app',
    'send_confirmation_email_task',
    'send_invitation_email_task', 
    'send_password_reset_email_task',
    'send_notification_to_all_users_task',
    'check_all_services_task',
    'update_service_metrics_task',
    'cleanup_expired_invitations_task',
    'send_invitation_reminder_task',
    'cleanup_old_submissions_task',
    'cleanup_inactive_users_task',
    'rotate_flags_task',
    'backup_database_task'
]