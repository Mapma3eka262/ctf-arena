from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.models import UserRole, ChallengeCategory, Difficulty, InvitationStatus, CheckType

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# Auth schemas
class UserBase(BaseSchema):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    team_name: Optional[str] = None

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    role: UserRole
    team_id: Optional[UUID]
    is_active: bool
    created_at: datetime

class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseSchema):
    user_id: Optional[UUID] = None
    username: Optional[str] = None

class PasswordResetRequest(BaseSchema):
    email: EmailStr

class PasswordReset(BaseSchema):
    token: str
    new_password: str

# Team schemas
class TeamBase(BaseSchema):
    name: str
    avatar_url: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: UUID
    score: int
    max_size: int
    created_at: datetime
    members: List[UserResponse]

class InvitationBase(BaseSchema):
    email: EmailStr

class InvitationCreate(InvitationBase):
    pass

class InvitationResponse(InvitationBase):
    id: UUID
    team_id: UUID
    token: str
    status: InvitationStatus
    expires_at: datetime
    created_by: UUID
    created_at: datetime

# Challenge schemas
class Hint(BaseSchema):
    id: str
    text: str
    cost: int
    unlocked_count: int = 0

class File(BaseSchema):
    id: str
    filename: str
    url: str
    size: int

class ChallengeBase(BaseSchema):
    title: str
    description: str
    category: ChallengeCategory
    difficulty: Difficulty
    initial_points: int
    min_points: int = 50
    author: str
    is_active: bool = True
    hints: List[Hint] = []
    files: List[File] = []

class ChallengeCreate(ChallengeBase):
    flag: str

class ChallengeResponse(ChallengeBase):
    id: UUID
    points: int
    solves_count: int
    created_at: datetime

class ChallengeDetailedResponse(ChallengeResponse):
    unlocked_hints: List[Hint] = []

class ChallengeSolveResponse(BaseSchema):
    id: UUID
    challenge_id: UUID
    team_id: UUID
    solved_at: datetime
    points_earned: int

# Submission schemas
class SubmissionBase(BaseSchema):
    challenge_id: UUID
    flag: str

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(BaseSchema):
    id: UUID
    challenge_id: UUID
    team_id: UUID
    user_id: UUID
    flag: str
    is_correct: bool
    submitted_at: datetime

class SubmissionStats(BaseSchema):
    total_submissions: int
    correct_submissions: int
    success_rate: float

class LeaderboardEntry(BaseSchema):
    team_id: UUID
    team_name: str
    score: int
    last_solve: Optional[datetime]
    solve_count: int

# Monitoring schemas
class ServiceBase(BaseSchema):
    name: str
    host: str
    port: int
    check_type: CheckType
    expected_status: int = 200
    check_interval: int = 30
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: UUID

class ServiceStatusResponse(BaseSchema):
    id: UUID
    service_id: UUID
    is_up: bool
    response_time: Optional[float]
    last_check: datetime
    error_message: Optional[str]

class ServiceWithStatus(ServiceResponse):
    current_status: Optional[ServiceStatusResponse]

# Admin schemas
class AdminStats(BaseSchema):
    total_users: int
    total_teams: int
    total_challenges: int
    total_submissions: int
    active_users_24h: int
    correct_submissions_rate: float

class UserUpdateAdmin(BaseSchema):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
