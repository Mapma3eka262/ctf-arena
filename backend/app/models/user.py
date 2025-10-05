from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='member')  # 'admin', 'captain', 'member'
    team_id = Column(Integer, ForeignKey('teams.id'))
    language = Column(String(2), default='ru')  # 'ru', 'en'
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    team = relationship("Team", back_populates="members")
    submissions = relationship("Submission", back_populates="user")
    sent_invitations = relationship("TeamInvite", foreign_keys="TeamInvite.invited_by", back_populates="inviter")