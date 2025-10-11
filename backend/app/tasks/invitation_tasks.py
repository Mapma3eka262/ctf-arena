# backend/app/tasks/invitation_tasks.py
from app.tasks.celery import celery_app
from app.core.database import SessionLocal
from app.services.invitation_service import InvitationService

@celery_app.task
def cleanup_expired_invitations_task():
    """Очистка просроченных приглашений"""
    db = SessionLocal()
    invitation_service = InvitationService(db)
    
    try:
        cleaned_count = invitation_service.cleanup_expired_invitations()
        print(f"Очищено {cleaned_count} просроченных приглашений")
        return {"cleaned_count": cleaned_count}
    except Exception as e:
        print(f"Ошибка при очистке приглашений: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def send_invitation_reminder_task(invitation_id: int):
    """Отправка напоминания о приглашении"""
    from app.models.invitation import Invitation
    from app.services.email_service import EmailService
    
    db = SessionLocal()
    email_service = EmailService()
    
    try:
        invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
        if invitation and invitation.status == "pending":
            subject = f"Напоминание: приглашение в команду {invitation.team.name}"
            body = f"""
            Это напоминание о приглашении присоединиться к команде "{invitation.team.name}".
            
            Приглашение истекает {invitation.expires_at.strftime('%d.%m.%Y %H:%M')}.
            
            Для принятия приглашения войдите в систему CyberCTF Arena.
            """
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                email_service._send_email(invitation.email, subject, body)
            )
            loop.close()
            
    except Exception as e:
        print(f"Ошибка при отправке напоминания: {e}")
    finally:
        db.close()