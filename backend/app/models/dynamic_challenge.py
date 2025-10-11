# backend/app/models/dynamic_challenge.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class DynamicChallenge(Base):
    __tablename__ = "dynamic_challenges"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), unique=True)
    
    # Конфигурация Docker
    docker_image = Column(String(255), nullable=False)
    instance_config = Column(JSON, nullable=False)  # { "internal_port": 80, "environment": {} }
    resource_limits = Column(JSON, nullable=False)  # { "memory": "100m", "cpu": 1024 }
    
    # Настройки инстансов
    reset_interval = Column(Integer, default=3600)  # секунды
    max_instances = Column(Integer, default=10)
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Связи
    challenge = relationship("Challenge", back_populates="dynamic_challenge")
    instances = relationship("ChallengeInstance", back_populates="dynamic_challenge")
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChallengeInstance(Base):
    __tablename__ = "challenge_instances"

    id = Column(Integer, primary_key=True, index=True)
    dynamic_challenge_id = Column(Integer, ForeignKey("dynamic_challenges.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Docker информация
    container_id = Column(String(64), nullable=False)
    host_port = Column(Integer, nullable=False)
    internal_port = Column(Integer, nullable=False)
    
    # Флаг и статус
    flag = Column(String(500), nullable=False)
    status = Column(String(20), default="running")  # running, stopped, error
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    last_health_check = Column(DateTime)
    
    # Связи
    dynamic_challenge = relationship("DynamicChallenge", back_populates="instances")
    team = relationship("Team")
