from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User, Submission, Team, ChallengeSolve
from app.schemas import SubmissionCreate, SubmissionResponse, SubmissionStats, LeaderboardEntry

router = APIRouter()

@router.post("/", response_model=SubmissionResponse)
def submit_flag(
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be in a team to submit flags"
        )
    
    # Rate limiting check (simplified)
    recent_submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team_id,
        Submission.submitted_at >= datetime.utcnow() - timedelta(minutes=1)
    ).count()
    
    if recent_submissions >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: 10 submissions per minute"
        )
    
    from app.services import ChallengeService
    try:
        submission = ChallengeService.submit_flag(
            db, submission_data, current_user.team_id, current_user.id
        )
        return submission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/team", response_model=List[SubmissionResponse])
def get_team_submissions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.team_id:
        return []
    
    submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team_id
    ).order_by(Submission.submitted_at.desc()).offset(skip).limit(limit).all()
    
    return submissions

@router.get("/stats", response_model=SubmissionStats)
def get_submission_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.team_id:
        return SubmissionStats(
            total_submissions=0,
            correct_submissions=0,
            success_rate=0.0
        )
    
    total = db.query(Submission).filter(
        Submission.team_id == current_user.team_id
    ).count()
    
    correct = db.query(Submission).filter(
        Submission.team_id == current_user.team_id,
        Submission.is_correct == True
    ).count()
    
    success_rate = correct / total if total > 0 else 0.0
    
    return SubmissionStats(
        total_submissions=total,
        correct_submissions=correct,
        success_rate=success_rate
    )

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    db: Session = Depends(get_db)
):
    teams = db.query(Team).filter(Team.score > 0).all()
    
    leaderboard = []
    for team in teams:
        # Get last solve time
        last_solve = db.query(ChallengeSolve).filter(
            ChallengeSolve.team_id == team.id
        ).order_by(ChallengeSolve.solved_at.desc()).first()
        
        solve_count = db.query(ChallengeSolve).filter(
            ChallengeSolve.team_id == team.id
        ).count()
        
        leaderboard.append(LeaderboardEntry(
            team_id=team.id,
            team_name=team.name,
            score=team.score,
            last_solve=last_solve.solved_at if last_solve else None,
            solve_count=solve_count
        ))
    
    # Sort by score (descending) and last solve time (ascending)
    leaderboard.sort(key=lambda x: (-x.score, x.last_solve or datetime.min))
    
    return leaderboard