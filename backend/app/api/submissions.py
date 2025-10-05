from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Submission
from app.services.flag_service import FlagService

router = APIRouter()

@router.post("/")
async def submit_flag(
    challenge_id: int,
    flag: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return FlagService.submit_flag(
        db, current_user.id, current_user.team_id, challenge_id, flag
    )

@router.get("/")
async def get_submissions(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return FlagService.get_team_submissions(db, current_user.team_id, limit)

@router.get("/stats")
async def get_submission_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return FlagService.get_submission_stats(db, current_user.team_id)

@router.get("/team")
async def get_team_submissions(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team_id
    ).order_by(Submission.submitted_at.desc()).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "challenge_title": s.challenge.title if s.challenge else "Unknown",
            "flag": s.flag,
            "status": s.status,
            "submitted_at": s.submitted_at,
            "points_awarded": s.points_awarded,
            "is_first_blood": s.is_first_blood
        }
        for s in submissions
    ]