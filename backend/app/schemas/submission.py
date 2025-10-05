from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubmissionBase(BaseModel):
    challenge_id: int
    flag: str

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    team_id: int
    challenge_id: int
    challenge_title: str
    flag: str
    status: str
    submitted_at: datetime
    points_awarded: int
    is_first_blood: bool
    
    class Config:
        from_attributes = True

class SubmissionStats(BaseModel):
    total: int
    accepted: int
    rejected: int
    pending: int
    success_rate: float

class FirstBlood(BaseModel):
    challenge_id: int
    challenge_title: str
    team_name: str
    user_name: str
    submitted_at: datetime