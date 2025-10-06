from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None

class TeamMember(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    joined_at: datetime

class TeamResponse(TeamBase):
    id: int
    score: int
    created_at: datetime
    members: List[TeamMember]

    class Config:
        from_attributes = True

class TeamInvite(BaseModel):
    email: EmailStr