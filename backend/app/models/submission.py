from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    challenge_id = Column(Integer, ForeignKey('challenges.id'), nullable=False)
    flag = Column(String(500), nullable=False)
    status = Column(String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    submitted_at = Column(DateTime, default=datetime.utcnow)
    points_awarded = Column(Integer, default=0)
    is_first_blood = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="submissions")
    team = relationship("Team", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")