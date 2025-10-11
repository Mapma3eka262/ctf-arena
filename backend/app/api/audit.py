# backend/app/api/audit.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/logs")
async def get_audit_logs(
    user_id: int = Query(None, description="Фильтр по пользователю"),
    action: str = Query(None, description="Фильтр по действию"),
    resource_type: str = Query(None, description="Фильтр по типу ресурса"),
    limit: int = Query(100, description="Лимит записей"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение логов аудита (только для администраторов)"""
    audit_service = AuditService(db)
    logs = audit_service.get_audit_logs(user_id, action, resource_type, limit)
    
    return {
        "logs": logs,
        "total": len(logs)
    }

@router.get("/security-events")
async def get_security_events(
    severity: str = Query(None, description="Фильтр по серьезности"),
    limit: int = Query(50, description="Лимит записей"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение событий безопасности (только для администраторов)"""
    audit_service = AuditService(db)
    
    # Фильтрация по событиям безопасности
    logs = audit_service.get_audit_logs(
        resource_type="security",
        limit=limit
    )
    
    if severity:
        logs = [log for log in logs if log["severity"] == severity]
    
    return {
        "events": logs,
        "total": len(logs)
    }