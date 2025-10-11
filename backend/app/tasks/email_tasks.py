# backend/app/tasks/email_tasks.py
from app.tasks.celery import celery_app
from app.services.email_service import EmailService

@celery_app.task
def send_confirmation_email_task(email: str, username: str):
    """Фоновая задача отправки email подтверждения"""
    email_service = EmailService()
    
    # Имитация асинхронной отправки
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(
            email_service.send_confirmation_email(email, username)
        )
    finally:
        loop.close()

@celery_app.task
def send_invitation_email_task(email: str, team_name: str, inviter_name: str):
    """Фоновая задача отправки приглашения"""
    email_service = EmailService()
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(
            email_service.send_invitation_email(email, team_name, inviter_name)
        )
    finally:
        loop.close()

@celery_app.task
def send_password_reset_email_task(email: str, reset_token: str):
    """Фоновая задача отправки сброса пароля"""
    email_service = EmailService()
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(
            email_service.send_password_reset_email(email, reset_token)
        )
    finally:
        loop.close()

@celery_app.task
def send_notification_to_all_users_task(subject: str, message: str):
    """Рассылка уведомлений всем пользователям"""
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.services.email_service import EmailService
    
    db = SessionLocal()
    email_service = EmailService()
    
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for user in users:
            try:
                loop.run_until_complete(
                    email_service._send_email(user.email, subject, message)
                )
            except Exception as e:
                print(f"Ошибка отправки email пользователю {user.email}: {e}")
        
        loop.close()
        
    finally:
        db.close()