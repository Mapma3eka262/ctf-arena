from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserResponse

class TeamBase(BaseModel):
    name: str
    ip_address: Optional[str] = None

class TeamCreate(TeamBase):
    captain_username: str

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    score: int
    registration_date: datetime
    is_active: bool
    captain_id: int
    penalty_minutes: int
    extended_until: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamWithMembers(TeamResponse):
    members: List[UserResponse] = []
    captain: Optional[UserResponse] = None

class TeamRanking(BaseModel):
    rank: int
    team: TeamResponse
    score: int
    solved_challenges: int

class InviteRequest(BaseModel):
    email: EmailStr

class InviteResponse(BaseModel):
    id: int
    email: str
    status: str
    expires_at: datetime
    invited_by: str