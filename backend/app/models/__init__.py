# backend/app/models/__init__.py
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.models.service import Service
from app.models.invitation import Invitation
from app.models.competition import Competition
from app.models.dynamic_challenge import DynamicChallenge, ChallengeInstance
from app.models.notification import Notification
from app.models.audit_log import AuditLog

__all__ = [
    'User',
    'Team', 
    'Challenge',
    'Submission',
    'Service',
    'Invitation',
    'Competition',
    'DynamicChallenge',
    'ChallengeInstance',
    'Notification',
    'AuditLog'
]