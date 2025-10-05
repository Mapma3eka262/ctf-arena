from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChallengeBase(BaseModel):
    title: str
    category: str
    points: int
    description: str

class ChallengeCreate(ChallengeBase):
    flag: str

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    points: Optional[int] = None
    description: Optional[str] = None
    flag: Optional[str] = None
    is_active: Optional[bool] = None

class ChallengeResponse(ChallengeBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChallengeWithSolved(ChallengeResponse):
    solved: bool = False
    solved_by_team: bool = False

class CategoryStats(BaseModel):
    category: str
    total_challenges: int
    solved_challenges: int
    total_points: int
    earned_points: int