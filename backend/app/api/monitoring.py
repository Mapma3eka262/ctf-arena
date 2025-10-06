from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.service import Service
from app.services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/services")
async def get_services_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статуса сервисов"""
    monitoring_service = MonitoringService(db)
    services = db.query(Service).all()
    
    service_status = []
    for service in services:
        status = monitoring_service.check_service_status(service)
        service_status.append({
            "id": service.id,
            "name": service.name,
            "type": service.type,
            "host": service.host,
            "port": service.port,
            "status": status,
            "last_checked": service.last_checked
        })
    
    return service_status