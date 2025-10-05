from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))  # 'WEB', 'Crypto', 'Forensics', 'Reversing', 'PWN', 'MISC'
    points = Column(Integer, nullable=False)
    description = Column(Text)
    flag = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    submissions = relationship("Submission", back_populates="challenge")