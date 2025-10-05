from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Импорт всех моделей для правильной работы Alembic
from .user import User
from .team import Team
from .challenge import Challenge
from .submission import Submission
from .service import Service
from .invitation import TeamInvite
from .competition import Competition

__all__ = [
    'Base',
    'User',
    'Team', 
    'Challenge',
    'Submission',
    'Service',
    'TeamInvite',
    'Competition'
]