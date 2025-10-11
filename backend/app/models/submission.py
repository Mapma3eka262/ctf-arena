# backend/app/models/submission.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    flag = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False)  # pending, accepted, rejected
    points_awarded = Column(Integer, default=0)
    is_first_blood = Column(Boolean, default=False)
    
    # Внешние ключи
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    
    # Связи
    team = relationship("Team", back_populates="submissions")
    user = relationship("User")
    challenge = relationship("Challenge", back_populates="submissions")
    
    # Отметки времени
    submitted_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Submission(flag='{self.flag[:10]}...', status='{self.status}')>"