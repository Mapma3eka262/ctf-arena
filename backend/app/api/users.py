# backend/app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user

@router.get("/me/team")
async def get_current_user_team(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о команде текущего пользователя"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    return {
        "id": current_user.team.id,
        "name": current_user.team.name,
        "score": current_user.team.score,
        "description": current_user.team.description,
        "country": current_user.team.country,
        "created_at": current_user.team.created_at
    }

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о текущем пользователе"""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновление полей
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="user_update",
        resource_type="user",
        user_id=user.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о пользователе по ID"""
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра информации о пользователе"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка пользователей (только для администраторов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Активация пользователя (только для администраторов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    auth_service = AuthService(db)
    success = auth_service.activate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="user_activation",
        resource_type="user",
        details={"target_user_id": user_id}
    )
    
    return {"message": "Пользователь активирован"}