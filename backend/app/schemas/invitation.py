# backend/app/schemas/invitation.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class InvitationBase(BaseModel):
    email: EmailStr

class InvitationCreate(InvitationBase):
    team_id: int

class InvitationResponse(InvitationBase):
    id: int
    team_id: int
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True