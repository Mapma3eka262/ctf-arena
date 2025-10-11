# backend/app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.schemas.user import UserResponse
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate, ChallengeResponse
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/dashboard")
async def admin_dashboard(
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Панель управления администратора"""
    
    # Базовая статистика
    total_users = db.query(User).count()
    total_teams = db.query(Team).count()
    total_challenges = db.query(Challenge).filter(Challenge.is_active == True).count()
    total_submissions = db.query(Submission).count()
    
    # Активные пользователи (за последние 24 часа)
    from datetime import datetime, timedelta
    active_users = db.query(User).filter(
        User.last_login >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    # Статистика по категориям заданий
    category_stats = db.query(
        Challenge.category,
        Challenge.difficulty,
        Challenge.solved_count
    ).filter(Challenge.is_active == True).all()
    
    # Форматирование статистики по категориям
    categories = {}
    for category, difficulty, solved_count in category_stats:
        if category not in categories:
            categories[category] = {
                'total_challenges': 0,
                'total_solves': 0,
                'by_difficulty': {}
            }
        
        categories[category]['total_challenges'] += 1
        categories[category]['total_solves'] += solved_count
        categories[category]['by_difficulty'][difficulty] = categories[category]['by_difficulty'].get(difficulty, 0) + 1
    
    return {
        "statistics": {
            "total_users": total_users,
            "total_teams": total_teams,
            "total_challenges": total_challenges,
            "total_submissions": total_submissions,
            "active_users": active_users
        },
        "categories": categories,
        "recent_activity": await get_recent_activity(db)
    }

@router.get("/users", response_model=List[UserResponse])
async def admin_get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение списка всех пользователей (админ)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users/{user_id}/toggle")
async def admin_toggle_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Активация/деактивация пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    # Логирование
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="user_toggle",
        resource_type="user",
        details={
            "target_user_id": user_id,
            "new_status": "active" if user.is_active else "inactive"
        }
    )
    
    return {"message": f"Пользователь {'активирован' if user.is_active else 'деактивирован'}"}

@router.get("/teams")
async def admin_get_teams(
    skip: int = 0,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение списка всех команд (админ)"""
    teams = db.query(Team).offset(skip).limit(limit).all()
    
    result = []
    for team in teams:
        result.append({
            "id": team.id,
            "name": team.name,
            "score": team.score,
            "member_count": len(team.members),
            "country": team.country,
            "created_at": team.created_at
        })
    
    return {
        "teams": result,
        "total": db.query(Team).count()
    }

@router.delete("/teams/{team_id}")
async def admin_delete_team(
    team_id: int,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаление команды (админ)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Команда не найдена"
        )
    
    # Логирование перед удалением
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="team_deletion",
        resource_type="team",
        details={
            "team_id": team_id,
            "team_name": team.name,
            "member_count": len(team.members)
        }
    )
    
    db.delete(team)
    db.commit()
    
    return {"message": "Команда удалена"}

@router.post("/challenges", response_model=ChallengeResponse)
async def admin_create_challenge(
    challenge_data: ChallengeCreate,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание задания (админ)"""
    challenge = Challenge(**challenge_data.dict())
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    # Логирование
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="challenge_creation",
        resource_type="challenge",
        details={"challenge_id": challenge.id, "title": challenge.title}
    )
    
    return challenge

@router.put("/challenges/{challenge_id}", response_model=ChallengeResponse)
async def admin_update_challenge(
    challenge_id: int,
    challenge_update: ChallengeUpdate,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Обновление задания (админ)"""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено"
        )
    
    # Сохраняем старые значения для логов
    old_values = {
        "title": challenge.title,
        "points": challenge.points,
        "is_active": challenge.is_active
    }
    
    # Обновление полей
    update_data = challenge_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(challenge, field, value)
    
    db.commit()
    db.refresh(challenge)
    
    # Логирование
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="challenge_update",
        resource_type="challenge",
        details={
            "challenge_id": challenge_id,
            "old_values": old_values,
            "new_values": update_data
        }
    )
    
    return challenge

@router.post("/challenges/{challenge_id}/toggle")
async def admin_toggle_challenge(
    challenge_id: int,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Активация/деактивация задания"""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено"
        )
    
    challenge.is_active = not challenge.is_active
    db.commit()
    
    # Логирование
    audit_service = AuditService(db)
    await audit_service.log_admin_action(
        user_id=current_user.id,
        action="challenge_toggle",
        resource_type="challenge",
        details={
            "challenge_id": challenge_id,
            "new_status": "active" if challenge.is_active else "inactive"
        }
    )
    
    return {"message": f"Задание {'активировано' if challenge.is_active else 'деактивировано'}"}

@router.get("/submissions")
async def admin_get_submissions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение всех отправок (админ)"""
    query = db.query(Submission)
    
    if status:
        query = query.filter(Submission.status == status)
    
    submissions = query.order_by(Submission.submitted_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for submission in submissions:
        result.append({
            "id": submission.id,
            "team_name": submission.team.name,
            "username": submission.user.username,
            "challenge_title": submission.challenge.title,
            "flag": submission.flag[:20] + "..." if len(submission.flag) > 20 else submission.flag,
            "status": submission.status,
            "points_awarded": submission.points_awarded,
            "is_first_blood": submission.is_first_blood,
            "submitted_at": submission.submitted_at
        })
    
    return {
        "submissions": result,
        "total": query.count()
    }

async def get_recent_activity(db: Session) -> List[Dict[str, Any]]:
    """Получение последней активности для дашборда"""
    from datetime import datetime, timedelta
    
    # Последние регистрации
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    
    # Последние решения
    recent_solves = db.query(Submission).filter(
        Submission.status == 'accepted'
    ).order_by(Submission.submitted_at.desc()).limit(10).all()
    
    # Форматирование результатов
    users_activity = []
    for user in recent_users:
        users_activity.append({
            "type": "user_registration",
            "username": user.username,
            "timestamp": user.created_at,
            "team": user.team.name if user.team else "Без команды"
        })
    
    solves_activity = []
    for solve in recent_solves:
        solves_activity.append({
            "type": "challenge_solve",
            "team_name": solve.team.name,
            "username": solve.user.username,
            "challenge_title": solve.challenge.title,
            "points": solve.points_awarded,
            "timestamp": solve.submitted_at,
            "is_first_blood": solve.is_first_blood
        })
    
    # Объединяем и сортируем по времени
    all_activity = users_activity + solves_activity
    all_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return all_activity[:15]  # Возвращаем 15 последних событий
