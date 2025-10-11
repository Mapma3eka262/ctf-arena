# backend/app/services/audit_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

class AuditService:
    """Сервис для логирования событий безопасности"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_event(self,
                       action: str,
                       resource_type: str,
                       user_id: Optional[int] = None,
                       resource_id: Optional[int] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None,
                       severity: str = "info",
                       status: str = "success") -> AuditLog:
        """Логирование события аудита"""
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            severity=severity,
            status=status
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    async def log_user_login(self, user_id: int, ip_address: str, user_agent: str, status: str):
        """Логирование входа пользователя"""
        return await self.log_event(
            action="user_login",
            resource_type="user",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            severity="info" if status == "success" else "warning"
        )
    
    async def log_flag_submission(self, user_id: int, challenge_id: int, status: str, details: Dict):
        """Логирование отправки флага"""
        return await self.log_event(
            action="flag_submission",
            resource_type="challenge",
            user_id=user_id,
            resource_id=challenge_id,
            details=details,
            status=status,
            severity="info"
        )
    
    async def log_admin_action(self, user_id: int, action: str, resource_type: str, details: Dict):
        """Логирование действий администратора"""
        return await self.log_event(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            details=details,
            severity="info"
        )
    
    async def log_security_event(self, action: str, details: Dict, severity: str = "warning"):
        """Логирование событий безопасности"""
        return await self.log_event(
            action=action,
            resource_type="security",
            details=details,
            severity=severity,
            status="failure"
        )
    
    def get_audit_logs(self, 
                      user_id: Optional[int] = None,
                      action: Optional[str] = None,
                      resource_type: Optional[str] = None,
                      limit: int = 100) -> list:
        """Получение логов аудита"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]