from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class TeamInvite(Base):
    __tablename__ = "team_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    email = Column(String(100), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    invited_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')  # 'pending', 'accepted', 'expired'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="sent_invitations")