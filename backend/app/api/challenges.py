from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.challenge import Challenge
from app.models.submission import Submission

router = APIRouter()

@router.get("/")
async def get_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка заданий"""
    challenges = db.query(Challenge).filter(Challenge.is_active == True).all()
    
    # Получаем статусы решений для текущей команды
    team_submissions = {}
    if current_user.team:
        submissions = db.query(Submission).filter(
            Submission.team_id == current_user.team.id
        ).all()
        team_submissions = {sub.challenge_id: sub.status for sub in submissions}
    
    return [
        {
            "id": challenge.id,
            "title": challenge.title,
            "category": challenge.category,
            "description": challenge.description,
            "points": challenge.points,
            "difficulty": challenge.difficulty,
            "is_solved": team_submissions.get(challenge.id) == "accepted",
            "solved_count": challenge.solved_count,
            "first_blood_user": challenge.first_blood_user
        }
        for challenge in challenges
    ]

@router.get("/{challenge_id}")
async def get_challenge_detail(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации о задании"""
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    return {
        "id": challenge.id,
        "title": challenge.title,
        "category": challenge.category,
        "description": challenge.description,
        "points": challenge.points,
        "difficulty": challenge.difficulty,
        "hint": challenge.hint,
        "files": challenge.files,
        "created_at": challenge.created_at,
        "solved_count": challenge.solved_count
    }