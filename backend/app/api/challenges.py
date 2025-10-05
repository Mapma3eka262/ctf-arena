from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Challenge, Submission
from app.schemas.challenge import ChallengeResponse, ChallengeWithSolved

router = APIRouter()

@router.get("/", response_model=List[ChallengeWithSolved])
async def get_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Список активных заданий"""
    challenges = db.query(Challenge).filter(Challenge.is_active == True).all()
    
    result = []
    for challenge in challenges:
        # Проверяем, решила ли команда это задание
        solved = db.query(Submission).filter(
            Submission.challenge_id == challenge.id,
            Submission.team_id == current_user.team_id,
            Submission.status == 'accepted'
        ).first() is not None
        
        challenge_data = ChallengeWithSolved(
            id=challenge.id,
            title=challenge.title,
            category=challenge.category,
            points=challenge.points,
            description=challenge.description,
            is_active=challenge.is_active,
            created_at=challenge.created_at,
            solved=solved
        )
        result.append(challenge_data)
    
    return result

@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Информация о задании"""
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    return challenge

@router.get("/categories", response_model=List[str])
async def get_categories(
    db: Session = Depends(get_db)
):
    """Список категорий"""
    categories = db.query(Challenge.category).distinct().all()
    return [category[0] for category in categories if category[0]]