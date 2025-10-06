from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    score = Column(Integer, default=0)
    avatar_url = Column(String(255))
    country = Column(String(50))
    website = Column(String(255))
    
    # Связи
    members = relationship("User", back_populates="team")
    submissions = relationship("Submission", back_populates="team")
    invitations = relationship("Invitation", back_populates="team")
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Team(name='{self.name}', score={self.score})>"