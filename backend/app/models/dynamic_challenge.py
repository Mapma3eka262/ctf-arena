# backend/app/models/dynamic_challenge.py
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DynamicChallenge(Base):
    """Модель для динамических заданий с изолированными инстансами"""
    __tablename__ = "dynamic_challenges"

    id = Column(Integer, ForeignKey('challenges.id'), primary_key=True)
    docker_image = Column(String(255), nullable=False)
    instance_config = Column(JSON, nullable=False)  # Конфигурация Docker
    deployment_script = Column(Text)  # Скрипт развертывания
    reset_interval = Column(Integer, default=3600)  # Интервал сброса в секундах
    max_instances = Column(Integer, default=50)  # Максимальное количество инстансов
    resource_limits = Column(JSON)  # Ограничения ресурсов
    
    # Связь с базовым заданием
    challenge = relationship("Challenge", back_populates="dynamic_challenge")
    # Инстансы задания
    instances = relationship("ChallengeInstance", back_populates="dynamic_challenge")

class ChallengeInstance(Base):
    """Модель для инстансов динамических заданий"""
    __tablename__ = "challenge_instances"

    id = Column(Integer, primary_key=True)
    dynamic_challenge_id = Column(Integer, ForeignKey('dynamic_challenges.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    container_id = Column(String(64))  # ID Docker контейнера
    status = Column(String(20), default="creating")  # creating, running, stopped, error
    host_port = Column(Integer)  # Порт для доступа
    internal_port = Column(Integer)  # Внутренний порт контейнера
    flag = Column(String(500))  # Уникальный флаг для инстанса
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  # Время истечения инстанса
    last_health_check = Column(DateTime)
    
    # Связи
    dynamic_challenge = relationship("DynamicChallenge", back_populates="instances")
    team = relationship("Team")