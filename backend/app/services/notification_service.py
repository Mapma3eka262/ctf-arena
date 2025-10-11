# backend/app/services/notification_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.api.websocket import manager as websocket_manager

class NotificationService:
    """Сервис для управления уведомлениями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(self,
                                user_id: int,
                                title: str,
                                message: str,
                                notification_type: str = "info",
                                category: str = "system",
                                action_url: str = None,
                                metadata: Dict = None) -> Notification:
        """Создание нового уведомления"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            category=category,
            action_url=action_url,
            metadata=metadata or {}
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Отправляем уведомление через WebSocket если пользователь онлайн
        if user_id != 0:  # Не broadcast
            await websocket_manager.send_personal_message(user_id, {
                "type": "notification",
                "notification": notification.to_dict()
            })
        else:
            # Broadcast to all connected users
            await websocket_manager.broadcast_to_all({
                "type": "notification",
                "notification": notification.to_dict()
            })
        
        return notification
    
    async def send_team_notification(self,
                                   team_id: int,
                                   title: str,
                                   message: str,
                                   notification_type: str = "info") -> List[Notification]:
        """Отправка уведомления всем участникам команды"""
        from app.models.user import User
        
        team_members = self.db.query(User).filter(
            User.team_id == team_id,
            User.is_active == True
        ).all()
        
        notifications = []
        for member in team_members:
            notification = await self.create_notification(
                user_id=member.id,
                title=title,
                message=message,
                type=notification_type,
                category="team"
            )
            notifications.append(notification)
        
        return notifications
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Пометить уведомление как прочитанное"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        
        return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Получение уведомлений пользователя"""
        query = self.db.query(Notification).filter(
            (Notification.user_id == user_id) | (Notification.user_id == 0)
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
        
        return [notification.to_dict() for notification in notifications]