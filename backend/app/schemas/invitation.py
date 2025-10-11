# backend/app/schemas/invitation.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class InvitationBase(BaseModel):
    email: EmailStr
    status: str

class InvitationCreate(BaseModel):
    email: EmailStr

class InvitationResponse(InvitationBase):
    id: int
    team_id: int
    invited_by_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
