from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChallengeBase(BaseModel):
    title: str
    description: str
    category: str
    difficulty: str
    points: int
    hint: Optional[str] = None

class ChallengeCreate(ChallengeBase):
    flag: str
    files: Optional[str] = None

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    points: Optional[int] = None
    hint: Optional[str] = None
    is_active: Optional[bool] = None

class ChallengeResponse(ChallengeBase):
    id: int
    is_active: bool
    solved_count: int
    is_solved: bool = False
    created_at: datetime
    first_blood_user: Optional[str] = None

    class Config:
        from_attributes = True

class ChallengeDetail(ChallengeResponse):
    files: Optional[str] = None