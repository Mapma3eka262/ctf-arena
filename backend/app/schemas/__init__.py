# Backend schemas initialization
from app.schemas.auth import UserRegister, Token, TokenData
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.team import TeamBase, TeamCreate, TeamUpdate, TeamResponse, TeamInvite
from app.schemas.challenge import ChallengeBase, ChallengeCreate, ChallengeUpdate, ChallengeResponse
from app.schemas.submission import FlagSubmit, SubmissionBase, SubmissionResponse, SubmissionStats
from app.schemas.invitation import InvitationBase, InvitationCreate, InvitationResponse

__all__ = [
    'UserRegister', 'Token', 'TokenData',
    'UserBase', 'UserCreate', 'UserUpdate', 'UserResponse', 
    'TeamBase', 'TeamCreate', 'TeamUpdate', 'TeamResponse', 'TeamInvite',
    'ChallengeBase', 'ChallengeCreate', 'ChallengeUpdate', 'ChallengeResponse',
    'FlagSubmit', 'SubmissionBase', 'SubmissionResponse', 'SubmissionStats',
    'InvitationBase', 'InvitationCreate', 'InvitationResponse'
]
