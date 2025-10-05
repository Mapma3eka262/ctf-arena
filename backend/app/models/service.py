from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20))  # 'web', 'ssh', 'database'
    url = Column(String(500))  # URL для HTTP проверки
    status = Column(String(20), default='offline')  # 'online', 'offline'
    team_id = Column(Integer, ForeignKey('teams.id'))
    last_checked = Column(DateTime)
    last_status_change = Column(DateTime)
    
    team = relationship("Team", back_populates="services")