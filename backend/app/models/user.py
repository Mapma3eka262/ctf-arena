# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.security import get_password_hash

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_captain = Column(Boolean, default=False)
    
    # Связи
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="members")
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    joined_at = Column(DateTime, default=func.now())

    def set_password(self, password: str):
        """Установка хешированного пароля"""
        self.hashed_password = get_password_hash(password)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"