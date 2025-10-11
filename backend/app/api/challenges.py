# backend/app/api/challenges.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.challenge import ChallengeResponse, ChallengeDetail
from app.models.challenge import Challenge
from app.models.submission import Submission

router = APIRouter()

@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    category: str = None,
    difficulty: str = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка заданий"""
    query = db.query(Challenge).filter(Challenge.is_visible == True)
    
    if category:
        query = query.filter(Challenge.category == category)
    
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)
    
    challenges = query.order_by(Challenge.points.asc()).all()
    
    # Добавляем информацию о решении для текущего пользователя
    response_challenges = []
    for challenge in challenges:
        challenge_data = ChallengeResponse.from_orm(challenge)
        
        # Проверяем, решил ли пользователь это задание
        if current_user.team:
            solved = db.query(Submission).filter(
                Submission.team_id == current_user.team_id,
                Submission.challenge_id == challenge.id,
                Submission.status == 'accepted'
            ).first()
            challenge_data.is_solved = solved is not None
        else:
            challenge_data.is_solved = False
        
        response_challenges.append(challenge_data)
    
    return response_challenges

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db)
):
    """Получение списка категорий заданий"""
    categories = db.query(Challenge.category).distinct().all()
    return [category[0] for category in categories]

@router.get("/{challenge_id}", response_model=ChallengeDetail)
async def get_challenge(
    challenge_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение детальной информации о задании"""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено"
        )
    
    if not challenge.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не доступно"
        )
    
    # Проверяем, решил ли пользователь это задание
    is_solved = False
    if current_user.team:
        solved = db.query(Submission).filter(
            Submission.team_id == current_user.team_id,
            Submission.challenge_id == challenge.id,
            Submission.status == 'accepted'
        ).first()
        is_solved = solved is not None
    
    challenge_data = ChallengeDetail.from_orm(challenge)
    challenge_data.is_solved = is_solved
    
    return challenge_data

@router.get("/{challenge_id}/solves")
async def get_challenge_solves(
    challenge_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получение информации о решениях задания"""
    from app.models.submission import Submission
    from app.models.team import Team
    
    solves = db.query(Submission).filter(
        Submission.challenge_id == challenge_id,
        Submission.status == 'accepted'
    ).order_by(Submission.submitted_at.asc()).limit(limit).all()
    
    result = []
    for solve in solves:
        result.append({
            "team_name": solve.team.name,
            "solved_at": solve.submitted_at,
            "is_first_blood": solve.is_first_blood
        })
    
    return {
        "challenge_id": challenge_id,
        "solves": result,
        "total_solves": len(result)
    }

@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового задания (только для администраторов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    challenge = Challenge(**challenge_data.dict())
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    # Логирование события
    from app.services.audit_service import AuditService
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="challenge_creation",
        resource_type="challenge",
        details={"challenge_id": challenge.id, "title": challenge.title}
    )
    
    return challenge

@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(
    challenge_id: int,
    challenge_update: ChallengeUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление задания (только для администраторов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено"
        )
    
    # Обновление полей
    update_data = challenge_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(challenge, field, value)
    
    db.commit()
    db.refresh(challenge)
    
    # Логирование события
    from app.services.audit_service import AuditService
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="challenge_update",
        resource_type="challenge",
        details={"challenge_id": challenge_id, "updated_fields": list(update_data.keys())}
    )
    
    return challenge