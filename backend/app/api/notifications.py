# backend/app/api/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение уведомлений пользователя"""
    notification_service = NotificationService(db)
    notifications = notification_service.get_user_notifications(current_user.id, unread_only)
    
    return {
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n["is_read"]])
    }

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пометить уведомление как прочитанное"""
    notification_service = NotificationService(db)
    success = await notification_service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Уведомление не найдено"
        )
    
    return {"message": "Уведомление помечено как прочитанное"}

@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пометить все уведомления как прочитанные"""
    notification_service = NotificationService(db)
    notifications = notification_service.get_user_notifications(current_user.id, unread_only=True)
    
    for notification in notifications:
        await notification_service.mark_as_read(notification["id"], current_user.id)
    
    return {"message": "Все уведомления помечены как прочитанные"}