from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.models import Base

class Competition(Base):
    __tablename__ = "competitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=False)
    penalty_minutes = Column(Integer, default=30)
    service_check_interval = Column(Integer, default=3)
    max_team_size = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)