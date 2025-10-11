# backend/app/schemas/submission.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FlagSubmit(BaseModel):
    challenge_id: int
    flag: str

class SubmissionBase(BaseModel):
    flag: str
    status: str

class SubmissionResponse(BaseModel):
    id: int
    challenge_title: str
    flag: str
    status: str
    points_awarded: int
    submitted_at: datetime
    is_first_blood: bool

    class Config:
        from_attributes = True

class SubmissionStats(BaseModel):
    total: int
    accepted: int
    rejected: int
    success_rate: float