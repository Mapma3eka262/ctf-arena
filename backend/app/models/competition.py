from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.core.database import Base

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rules = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Настройки
    max_team_size = Column(Integer, default=5)
    scoring_type = Column(String(20), default="dynamic")  # static, dynamic
    allowed_categories = Column(Text)  # JSON список разрешенных категорий
    
    # Отметки времени
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def is_running(self) -> bool:
        """Проверка, идет ли соревнование сейчас"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time and self.is_active

    def __repr__(self):
        return f"<Competition(name='{self.name}')>"