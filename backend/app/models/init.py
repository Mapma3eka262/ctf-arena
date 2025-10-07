# Backend models initialization
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.models.service import Service
from app.models.invitation import Invitation
from app.models.competition import Competition

__all__ = [
    'User',
    'Team', 
    'Challenge',
    'Submission',
    'Service',
    'Invitation',
    'Competition'
]
