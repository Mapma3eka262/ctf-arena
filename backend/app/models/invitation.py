# backend/app/models/invitation.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.core.database import Base

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, expired
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    
    # Внешние ключи
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Связи
    team = relationship("Team", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def is_expired(self) -> bool:
        """Проверка истечения срока действия приглашения"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<Invitation(email='{self.email}', status='{self.status}')>"