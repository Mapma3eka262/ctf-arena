# backend/app/tasks/monitoring_tasks.py
from app.tasks.celery import celery_app
from app.core.database import SessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.telegram_service import TelegramService

@celery_app.task
def check_all_services_task():
    """Периодическая проверка всех сервисов"""
    db = SessionLocal()
    monitoring_service = MonitoringService(db)
    telegram_service = TelegramService()
    
    try:
        results = monitoring_service.check_all_services()
        
        # Отправляем уведомление о проблемах
        offline_services = [r for r in results if r['status'] == 'offline']
        if offline_services:
            message = "🔴 <b>Обнаружены проблемы с сервисами:</b>\n\n"
            for service in offline_services:
                message += f"• {service['service']} - offline\n"
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_service.send_notification(message))
            loop.close()
        
        return {
            "checked_services": len(results),
            "online": len([r for r in results if r['status'] == 'online']),
            "offline": len(offline_services)
        }
        
    except Exception as e:
        print(f"Ошибка при проверке сервисов: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def update_service_metrics_task():
    """Обновление метрик сервисов"""
    db = SessionLocal()
    
    try:
        from app.models.service import Service
        from datetime import datetime
        
        services = db.query(Service).all()
        
        for service in services:
            # Здесь можно добавить логику сбора метрик
            # например, использование CPU, памяти и т.д.
            pass
            
        db.commit()
        
    except Exception as e:
        print(f"Ошибка при обновлении метрик: {e}")
    finally:
        db.close()