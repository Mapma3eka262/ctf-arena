from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models import User, Challenge, ChallengeCategory, Difficulty
from app.schemas import ChallengeResponse, ChallengeDetailedResponse

router = APIRouter()

@router.get("/", response_model=List[ChallengeResponse])
def get_challenges(
    category: Optional[ChallengeCategory] = None,
    difficulty: Optional[Difficulty] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Challenge).filter(Challenge.is_active == True)
    
    if category:
        query = query.filter(Challenge.category == category)
    
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)
    
    challenges = query.order_by(Challenge.points.desc()).all()
    return challenges

@router.get("/{challenge_id}", response_model=ChallengeDetailedResponse)
def get_challenge(
    challenge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if not challenge.is_active and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # In a real implementation, you would check which hints the team has unlocked
    response_data = ChallengeDetailedResponse.from_orm(challenge)
    response_data.unlocked_hints = []  # Add logic to determine unlocked hints
    
    return response_data

@router.post("/{challenge_id}/hints/{hint_id}")
def unlock_hint(
    challenge_id: UUID,
    hint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be in a team to unlock hints"
        )
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Find the hint
    hint = None
    for h in challenge.hints:
        if h.get('id') == hint_id:
            hint = h
            break
    
    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hint not found"
        )
    
    # Check if hint is already unlocked (implement your logic)
    # Deduct points from team (implement your logic)
    
    return {"hint": hint}

@router.get("/{challenge_id}/files/{file_id}")
def download_file(
    challenge_id: UUID,
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Find the file
    file_info = None
    for f in challenge.files:
        if f.get('id') == file_id:
            file_info = f
            break
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # In a real implementation, you would serve the file
    return {"message": "File download endpoint", "file": file_info}