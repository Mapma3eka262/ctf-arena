# backend/app/api/submissions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.submission import FlagSubmit, SubmissionResponse, SubmissionStats
from app.schemas.user import UserResponse
from app.models.submission import Submission
from app.models.challenge import Challenge
from app.services.flag_service import FlagService
from app.services.scoring_service import ScoringService
from app.services.audit_service import AuditService
from app.services.telegram_service import TelegramService
from app.api.websocket import manager as websocket_manager

router = APIRouter()

@router.post("/", response_model=SubmissionResponse)
async def submit_flag(
    flag_data: FlagSubmit,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка флага для проверки"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для отправки флагов необходимо состоять в команде"
        )
    
    # Проверка rate limiting
    from app.core.rate_limiting import rate_limiter
    if await rate_limiter.is_rate_limited(
        identifier=str(current_user.id),
        limit=30,  # 30 попыток в минуту
        window=60,
        action="flag_submission"
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток. Попробуйте позже."
        )
    
    # Проверка существования задания
    challenge = db.query(Challenge).filter(
        Challenge.id == flag_data.challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено или неактивно"
        )
    
    # Проверка, не решено ли уже задание командой
    existing_solve = db.query(Submission).filter(
        Submission.team_id == current_user.team_id,
        Submission.challenge_id == flag_data.challenge_id,
        Submission.status == 'accepted'
    ).first()
    
    if existing_solve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ваша команда уже решила это задание"
        )
    
    flag_service = FlagService(db)
    scoring_service = ScoringService(db)
    audit_service = AuditService(db)
    telegram_service = TelegramService()
    
    # Проверка флага
    is_correct = flag_service.verify_flag(flag_data.challenge_id, flag_data.flag)
    
    # Создание записи об отправке
    submission = Submission(
        team_id=current_user.team_id,
        user_id=current_user.id,
        challenge_id=flag_data.challenge_id,
        flag=flag_data.flag,
        status='accepted' if is_correct else 'rejected',
        points_awarded=challenge.points if is_correct else 0
    )
    
    db.add(submission)
    db.flush()  # Получаем ID до коммита
    
    if is_correct:
        # Начисление очков и проверка first blood
        is_first_blood = scoring_service.award_points(
            current_user.team_id,
            flag_data.challenge_id,
            current_user.id
        )
        
        submission.is_first_blood = is_first_blood
        
        # Обновление статистики задания
        challenge.solved_count += 1
        if is_first_blood:
            challenge.first_blood_user_id = current_user.id
        
        # Отправка уведомлений через WebSocket
        await websocket_manager.broadcast_to_team(current_user.team_id, {
            "type": "team_flag_submitted",
            "user_id": current_user.id,
            "username": current_user.username,
            "challenge_id": flag_data.challenge_id,
            "challenge_title": challenge.title,
            "points": challenge.points,
            "is_first_blood": is_first_blood,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Отправка уведомления в Telegram о first blood
        if is_first_blood:
            await telegram_service.send_first_blood_notification(
                current_user.username,
                challenge.title,
                current_user.team.name
            )
    
    db.commit()
    db.refresh(submission)
    
    # Логирование события
    await audit_service.log_flag_submission(
        user_id=current_user.id,
        challenge_id=flag_data.challenge_id,
        status='accepted' if is_correct else 'rejected',
        details={
            "submission_id": submission.id,
            "is_first_blood": submission.is_first_blood if is_correct else False
        }
    )
    
    # Отправка уведомления в Telegram
    await telegram_service.send_flag_submission_notification(
        current_user.username,
        challenge.title,
        'accepted' if is_correct else 'rejected'
    )
    
    # Формирование ответа
    return SubmissionResponse(
        id=submission.id,
        challenge_title=challenge.title,
        flag=submission.flag[:10] + '...' if len(submission.flag) > 10 else submission.flag,
        status=submission.status,
        points_awarded=submission.points_awarded,
        submitted_at=submission.submitted_at,
        is_first_blood=submission.is_first_blood
    )

@router.get("/team", response_model=List[SubmissionResponse])
async def get_team_submissions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение истории отправок команды"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    submissions = db.query(Submission).filter(
        Submission.team_id == current_user.team_id
    ).order_by(Submission.submitted_at.desc()).limit(50).all()
    
    result = []
    for submission in submissions:
        result.append(SubmissionResponse(
            id=submission.id,
            challenge_title=submission.challenge.title,
            flag=submission.flag[:10] + '...' if len(submission.flag) > 10 else submission.flag,
            status=submission.status,
            points_awarded=submission.points_awarded,
            submitted_at=submission.submitted_at,
            is_first_blood=submission.is_first_blood
        ))
    
    return result

@router.get("/stats", response_model=SubmissionStats)
async def get_submission_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики отправок"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не состоит в команде"
        )
    
    total = db.query(Submission).filter(
        Submission.team_id == current_user.team_id
    ).count()
    
    accepted = db.query(Submission).filter(
        Submission.team_id == current_user.team_id,
        Submission.status == 'accepted'
    ).count()
    
    rejected = total - accepted
    
    success_rate = (accepted / total * 100) if total > 0 else 0
    
    return SubmissionStats(
        total=total,
        accepted=accepted,
        rejected=rejected,
        success_rate=round(success_rate, 2)
    )

@router.get("/recent")
async def get_recent_submissions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получение последних отправок (публичный endpoint)"""
    from app.models.team import Team
    from app.models.user import User
    
    submissions = db.query(Submission).join(Team).join(User).filter(
        Submission.status == 'accepted'
    ).order_by(Submission.submitted_at.desc()).limit(limit).all()
    
    result = []
    for submission in submissions:
        result.append({
            "id": submission.id,
            "team_name": submission.team.name,
            "username": submission.user.username,
            "challenge_title": submission.challenge.title,
            "points": submission.points_awarded,
            "is_first_blood": submission.is_first_blood,
            "submitted_at": submission.submitted_at
        })
    
    return {
        "submissions": result,
        "total": len(result)
    }
