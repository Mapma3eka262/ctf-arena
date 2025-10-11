# backend/app/schemas/challenge.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChallengeBase(BaseModel):
    title: str
    description: str
    category: str
    difficulty: str
    points: int
    flag: str
    hint: Optional[str] = None
    files: Optional[str] = None
    is_active: bool = True
    is_visible: bool = True

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    points: Optional[int] = None
    flag: Optional[str] = None
    hint: Optional[str] = None
    files: Optional[str] = None
    is_active: Optional[bool] = None
    is_visible: Optional[bool] = None

class ChallengeResponse(ChallengeBase):
    id: int
    solved_count: int = 0
    is_solved: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChallengeDetail(ChallengeResponse):
    first_blood_user_id: Optional[int] = None
