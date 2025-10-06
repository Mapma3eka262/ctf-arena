from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # WEB, Crypto, Forensics, etc.
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    points = Column(Integer, nullable=False)
    flag = Column(String(500), nullable=False)
    hint = Column(Text)
    files = Column(Text)  # JSON список файлов
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    
    # Статистика
    solved_count = Column(Integer, default=0)
    first_blood_user_id = Column(Integer, ForeignKey("users.id"))
    first_blood_user = relationship("User", foreign_keys=[first_blood_user_id])
    
    # Связи
    submissions = relationship("Submission", back_populates="challenge")
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Challenge(title='{self.title}', points={self.points})>"