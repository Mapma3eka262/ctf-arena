from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    language: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    language: Optional[str] = None

class UserResponse(UserBase):
    id: int
    team_id: Optional[int]
    is_active: bool
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    team_name: Optional[str]
    score: Optional[int]
    language: str