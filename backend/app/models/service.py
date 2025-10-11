# backend/app/models/service.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.core.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # web, ssh, database, etc.
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    check_endpoint = Column(String(100))  # Для HTTP проверок
    expected_status = Column(Integer, default=200)
    is_active = Column(Boolean, default=True)
    
    # Статус
    status = Column(String(20), default="unknown")  # online, offline, unknown
    last_checked = Column(DateTime)
    response_time = Column(Integer)  # в миллисекундах
    error_message = Column(Text)
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Service(name='{self.name}', status='{self.status}')>"