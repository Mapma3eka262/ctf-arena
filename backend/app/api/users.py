from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@router.get("/me/team")
async def get_current_user_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о команде текущего пользователя"""
    if not current_user.team:
        raise HTTPException(status_code=404, detail="Пользователь не состоит в команде")
    
    return {
        "id": current_user.team.id,
        "name": current_user.team.name,
        "score": current_user.team.score,
        "members": [
            {
                "username": member.username,
                "email": member.email,
                "role": "captain" if member.is_captain else "member",
                "is_active": member.is_active
            }
            for member in current_user.team.members
        ]
    }

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о текущем пользователе"""
    # Логика обновления пользователя
    if user_data.email and user_data.email != current_user.email:
        # Проверка уникальности email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email уже используется")
        current_user.email = user_data.email
    
    db.commit()
    db.refresh(current_user)
    return current_user