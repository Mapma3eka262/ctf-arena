from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.challenge import Challenge
from app.schemas.submission import FlagSubmit
from app.services.flag_service import FlagService
from app.services.scoring_service import ScoringService

router = APIRouter()

@router.post("/")
async def submit_flag(
    flag_data: FlagSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка флага на проверку"""
    if not current_user.team:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в команде")
    
    flag_service = FlagService(db)
    scoring_service = ScoringService(db)
    
    # Проверяем существование задания
    challenge = db.query(Challenge).filter(
        Challenge.id == flag_data.challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    # Проверяем, не решено ли уже задание командой
    existing_submission = db.query(Submission).filter(
        Submission.team_id == current_user.team.id,
        Submission.challenge_id == flag_data.challenge_id,
        Submission.status == "accepted"
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="Задание уже решено")
    
    # Проверяем флаг
    is_correct = flag_service.verify_flag(flag_data.challenge_id, flag_data.flag)
    
    # Создаем запись об отправке
    submission = Submission(
        team_id=current_user.team.id,
        user_id=current_user.id,
        challenge_id=flag_data.challenge_id,
        flag=flag_data.flag,
        status="accepted" if is_correct else "rejected"
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Если флаг верный, начисляем очки
    if is_correct:
        is_first_blood = scoring_service.award_points(
            team_id=current_user.team.id,
            challenge_id=flag_data.challenge_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Флаг верный!",
            "points": challenge.points,
            "is_first_blood": is_first_blood,
            "status": "accepted"
        }
    else:
        return {
            "message": "Неверный флаг",
            "points": 0,
            "is_first_blood": False,
            "status": "rejected"
        }

@router.get("/team")
async def get_team_submissions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение истории отправок команды"""
    if not current_user.team:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в команде")
    
    submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team.id
    ).order_by(desc(Submission.submitted_at)).limit(limit).all()
    
    return [
        {
            "id": sub.id,
            "challenge_title": sub.challenge.title,
            "flag": sub.flag,
            "status": sub.status,
            "points_awarded": sub.points_awarded,
            "submitted_at": sub.submitted_at,
            "is_first_blood": sub.is_first_blood
        }
        for sub in submissions
    ]

@router.get("/stats")
async def get_submission_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики отправок команды"""
    if not current_user.team:
        raise HTTPException(status_code=400, detail="Пользователь не состоит в команде")
    
    submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team.id
    ).all()
    
    total = len(submissions)
    accepted = len([s for s in submissions if s.status == "accepted"])
    rejected = len([s for s in submissions if s.status == "rejected"])
    success_rate = (accepted / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "success_rate": success_rate
    }