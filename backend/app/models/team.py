from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    score = Column(Integer, default=0)
    ip_address = Column(String(45))
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    captain_id = Column(Integer, ForeignKey('users.id'))
    penalty_minutes = Column(Integer, default=0)
    extended_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("User", back_populates="team")
    captain = relationship("User", foreign_keys=[captain_id])
    submissions = relationship("Submission", back_populates="team")
    services = relationship("Service", back_populates="team")
    invitations = relationship("TeamInvite", back_populates="team")