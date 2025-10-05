import asyncio
import aiohttp
import asyncssh
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException
import logging

from app.models import Service, Team
from app.core.config import settings

logger = logging.getLogger(__name__)

class MonitoringService:
    
    @staticmethod
    async def check_http_service(service: Service) -> bool:
        """Проверка HTTP сервиса"""
        try:
            timeout = aiohttp.ClientTimeout(total=settings.SERVICE_CHECK_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(service.url) as response:
                    return 200 <= response.status < 300
        except Exception as e:
            logger.error(f"HTTP check failed for {service.name}: {e}")
            return False
    
    @staticmethod
    async def check_ssh_service(service: Service) -> bool:
        """Проверка SSH сервиса"""
        try:
            # Парсим URL для получения хоста и порта
            # Формат: ssh://hostname:port
            if service.url.startswith('ssh://'):
                url_parts = service.url[6:].split(':')
                hostname = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 22
                
                async with asyncssh.connect(hostname, port=port, timeout=settings.SERVICE_CHECK_TIMEOUT) as conn:
                    return True
            return False
        except Exception as e:
            logger.error(f"SSH check failed for {service.name}: {e}")
            return False
    
    @staticmethod
    async def check_database_service(service: Service) -> bool:
        """Проверка базы данных (упрощенная проверка порта)"""
        try:
            # Для демонстрации - просто проверяем доступность порта
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(service.url, 5432),
                timeout=settings.SERVICE_CHECK_TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            logger.error(f"Database check failed for {service.name}: {e}")
            return False
    
    @staticmethod
    async def check_service_status(service: Service) -> bool:
        """Проверка статуса сервиса в зависимости от типа"""
        if service.type == 'web':
            return await MonitoringService.check_http_service(service)
        elif service.type == 'ssh':
            return await MonitoringService.check_ssh_service(service)
        elif service.type == 'database':
            return await MonitoringService.check_database_service(service)
        else:
            logger.warning(f"Unknown service type: {service.type}")
            return False
    
    @staticmethod
    async def update_service_status(db: Session, service: Service, status: bool):
        """Обновление статуса сервиса в БД"""
        current_time = datetime.utcnow()
        old_status = service.status
        
        service.last_checked = current_time
        
        if status:
            service.status = 'online'
        else:
            service.status = 'offline'
        
        # Обновляем время изменения статуса, если статус изменился
        if old_status != service.status:
            service.last_status_change = current_time
            logger.info(f"Service {service.name} status changed from {old_status} to {service.status}")
        
        db.commit()
    
    @staticmethod
    async def check_all_services(db: Session):
        """Проверка всех сервисов"""
        services = db.query(Service).filter(Service.is_active == True).all()
        
        tasks = []
        for service in services:
            task = MonitoringService.check_single_service(db, service)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    @staticmethod
    async def check_single_service(db: Session, service: Service):
        """Проверка одного сервиса"""
        try:
            status = await MonitoringService.check_service_status(service)
            await MonitoringService.update_service_status(db, service, status)
        except Exception as e:
            logger.error(f"Error checking service {service.name}: {e}")
    
    @staticmethod
    def get_team_services(db: Session, team_id: int):
        """Получение сервисов команды"""
        return db.query(Service).filter(Service.team_id == team_id).all()
    
    @staticmethod
    def get_service_status_history(db: Session, service_id: int, hours: int = 24):
        """Получение истории статусов сервиса"""
        # В реальной системе здесь был бы отдельная таблица для истории статусов
        # Для демонстрации возвращаем фиктивные данные
        current_time = datetime.utcnow()
        history = []
        
        for i in range(hours):
            time_point = current_time - timedelta(hours=i)
            # В реальной системе здесь был бы запрос к таблице истории
            history.append({
                'timestamp': time_point,
                'status': 'online' if i % 4 != 0 else 'offline'  # Фиктивные данные
            })
        
        return history
    
    @staticmethod
    def get_services_health_summary(db: Session):
        """Получение сводки по здоровью сервисов"""
        services = db.query(Service).all()
        total = len(services)
        online = len([s for s in services if s.status == 'online'])
        offline = total - online
        
        return {
            'total_services': total,
            'online_services': online,
            'offline_services': offline,
            'health_percentage': (online / total * 100) if total > 0 else 0
        }