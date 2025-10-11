# backend/app/models/notification.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Notification(Base):
    """Модель для системных уведомлений"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # 0 = broadcast to all
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # info, warning, success, error
    category = Column(String(50), default="system")  # system, team, challenge
    is_read = Column(Boolean, default=False)
    action_url = Column(String(500))  # URL для действия
    metadata = Column(JSON)  # Дополнительные данные
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "category": self.category,
            "is_read": self.is_read,
            "action_url": self.action_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }