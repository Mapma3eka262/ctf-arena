# backend/app/models/audit_log.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    """Модель для логов аудита безопасности"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # NULL для системных событий
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    details = Column(JSON)
    severity = Column(String(20), default="info")  # info, warning, error, critical
    status = Column(String(20), default="success")  # success, failure

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "severity": self.severity,
            "status": self.status
        }