import time
import requests
import socket
from datetime import datetime, timedelta

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Service, ServiceStatus

# Celery app
celery_app = Celery(
    'ctf_tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task
def check_service_health():
    """Проверка доступности сервисов"""
    db = SessionLocal()
    try:
        services = db.query(Service).filter(Service.is_active == True).all()
        
        for service in services:
            status = perform_health_check(service)
            service_status = ServiceStatus(
                service_id=service.id,
                is_up=status['is_up'],
                response_time=status['response_time'],
                error_message=status['error_message']
            )
            db.add(service_status)
        
        db.commit()
    finally:
        db.close()

def perform_health_check(service):
    """Выполнить проверку здоровья сервиса"""
    start_time = time.time()
    
    try:
        if service.check_type == 'http':
            response = requests.get(
                f"http://{service.host}:{service.port}",
                timeout=10
            )
            is_up = response.status_code == service.expected_status
            error_message = None if is_up else f"HTTP {response.status_code}"
        
        elif service.check_type == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((service.host, service.port))
            is_up = result == 0
            error_message = None if is_up else f"TCP connection failed: {result}"
            sock.close()
        
        else:  # ssh
            # Simplified SSH check - in production use paramiko
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((service.host, service.port))
            is_up = result == 0
            error_message = None if is_up else f"SSH connection failed: {result}"
            sock.close()
    
    except Exception as e:
        is_up = False
        error_message = str(e)
    
    response_time = int((time.time() - start_time) * 1000)  # Convert to ms
    
    return {
        'is_up': is_up,
        'response_time': response_time if is_up else None,
        'error_message': error_message
    }

@celery_app.task
def cleanup_expired_data():
    """Очистка устаревших данных"""
    db = SessionLocal()
    try:
        # Clean up expired invitations
        expired_invitations = db.query(Invitation).filter(
            Invitation.status == InvitationStatus.PENDING,
            Invitation.expires_at < datetime.utcnow()
        )
        expired_invitations.update({'status': InvitationStatus.EXPIRED})
        
        # Clean up old service status records (keep only 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        old_statuses = db.query(ServiceStatus).filter(
            ServiceStatus.last_check < cutoff_time
        )
        old_statuses.delete()
        
        db.commit()
    finally:
        db.close()

@celery_app.task
def recalculate_scores():
    """Пересчет очков для всех заданий"""
    db = SessionLocal()
    try:
        challenges = db.query(Challenge).all()
        
        for challenge in challenges:
            challenge.points = ChallengeService.calculate_points(
                challenge.initial_points,
                challenge.solves_count,
                challenge.min_points
            )
        
        db.commit()
    finally:
        db.close()

# Celery beat schedule
celery_app.conf.beat_schedule = {
    'check-service-health-every-30s': {
        'task': 'app.workers.tasks.check_service_health',
        'schedule': 30.0,
    },
    'cleanup-expired-data-daily': {
        'task': 'app.workers.tasks.cleanup_expired_data',
        'schedule': 86400.0,  # 24 hours
    },
    'recalculate-scores-hourly': {
        'task': 'app.workers.tasks.recalculate_scores',
        'schedule': 3600.0,  # 1 hour
    },
}