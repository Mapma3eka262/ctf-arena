from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/services")
async def get_team_services(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение сервисов команды"""
    services = MonitoringService.get_team_services(db, current_user.team_id)
    
    return [
        {
            "id": service.id,
            "name": service.name,
            "type": service.type,
            "url": service.url,
            "status": service.status,
            "last_checked": service.last_checked,
            "last_status_change": service.last_status_change
        }
        for service in services
    ]

@router.get("/history")
async def get_service_history(
    service_id: int = None,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение истории статусов сервисов"""
    if service_id:
        # История конкретного сервиса
        history = MonitoringService.get_service_status_history(db, service_id, hours)
    else:
        # История всех сервисов команды
        services = MonitoringService.get_team_services(db, current_user.team_id)
        history = {}
        for service in services:
            history[service.name] = MonitoringService.get_service_status_history(db, service.id, hours)
    
    return history

@router.post("/services/{service_id}/check")
async def check_single_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ручная проверка сервиса"""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.team_id == current_user.team_id
    ).first()
    
    if not service:
        return {"error": "Service not found"}
    
    import asyncio
    await MonitoringService.check_single_service(db, service)
    
    return {"status": "checked", "service_status": service.status}