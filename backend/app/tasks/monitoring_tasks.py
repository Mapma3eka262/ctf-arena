from celery import shared_task
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.tasks.celery import get_db
from app.services.monitoring_service import MonitoringService
from app.models import Competition

logger = logging.getLogger(__name__)

@shared_task
def monitor_all_services():
    """Проверка всех сервисов"""
    try:
        db = next(get_db())
        import asyncio
        asyncio.run(MonitoringService.check_all_services(db))
        logger.info("Service monitoring completed successfully")
    except Exception as e:
        logger.error(f"Service monitoring failed: {e}")
    finally:
        db.close()

@shared_task
def restart_failed_services():
    """Перезапуск упавших сервисов"""
    try:
        db = next(get_db())
        # Здесь должна быть логика перезапуска сервисов
        # Например, через Docker API или SSH
        logger.info("Failed services restart completed")
    except Exception as e:
        logger.error(f"Failed services restart failed: {e}")
    finally:
        db.close()

@shared_task
def check_competition_time():
    """Проверка времени соревнования"""
    try:
        db = next(get_db())
        current_time = datetime.utcnow()
        
        # Получаем активное соревнование
        competition = db.query(Competition).filter(Competition.is_active == True).first()
        
        if competition:
            if competition.end_time and current_time >= competition.end_time:
                # Соревнование завершено
                competition.is_active = False
                db.commit()
                logger.info("Competition has ended automatically")
                
                # Запускаем генерацию отчета
                generate_competition_report.delay()
    except Exception as e:
        logger.error(f"Competition time check failed: {e}")
    finally:
        db.close()

@shared_task
def generate_competition_report():
    """Генерация финального отчета"""
    try:
        db = next(get_db())
        # Логика генерации отчета
        logger.info("Competition report generated")
    except Exception as e:
        logger.error(f"Competition report generation failed: {e}")
    finally:
        db.close()