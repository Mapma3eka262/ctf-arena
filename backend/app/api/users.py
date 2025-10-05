from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User

router = APIRouter()

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "team_id": current_user.team_id,
        "language": current_user.language,
        "is_active": current_user.is_active
    }

@router.get("/me/team")
async def get_user_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team:
        raise HTTPException(status_code=404, detail="User not in a team")
    
    team = current_user.team
    return {
        "id": team.id,
        "name": team.name,
        "score": team.score,
        "members": [
            {
                "id": member.id,
                "username": member.username,
                "email": member.email,
                "role": member.role,
                "is_active": member.is_active
            }
            for member in team.members
        ]
    }