# backend/app/api/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/team/insights")
async def get_team_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение аналитических данных по команде"""
    if not current_user.team:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не состоит в команде"
        )
    
    analytics_service = AnalyticsService(db)
    insights = await analytics_service.get_team_insights(current_user.team.id)
    
    return insights

@router.get("/global")
async def get_global_analytics(
    db: Session = Depends(get_db)
):
    """Получение глобальной статистики платформы"""
    analytics_service = AnalyticsService(db)
    stats = await analytics_service.get_global_statistics()
    
    return stats

@router.get("/team/activity")
async def get_team_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение данных об активности команды"""
    if not current_user.team:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не состоит в команде"
        )
    
    analytics_service = AnalyticsService(db)
    activity_patterns = await analytics_service.analyze_activity_patterns(current_user.team.id)
    
    return activity_patterns