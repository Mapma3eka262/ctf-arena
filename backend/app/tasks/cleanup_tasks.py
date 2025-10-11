# backend/app/tasks/cleanup_tasks.py
from app.tasks.celery import celery_app
from app.core.database import SessionLocal
from datetime import datetime, timedelta

@celery_app.task
def cleanup_old_submissions_task():
    """Очистка старых отправок флагов"""
    db = SessionLocal()
    
    try:
        from app.models.submission import Submission
        
        # Удаляем отправки старше 30 дней
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = db.query(Submission).filter(
            Submission.submitted_at < cutoff_date
        ).delete()
        
        db.commit()
        print(f"Удалено {deleted_count} старых отправок")
        return {"deleted_submissions": deleted_count}
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при очистке отправок: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def cleanup_inactive_users_task():
    """Очистка неактивных пользователей"""
    db = SessionLocal()
    
    try:
        from app.models.user import User
        
        # Находим пользователей, неактивных более 90 дней
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        inactive_users = db.query(User).filter(
            User.last_login < cutoff_date,
            User.is_active == True
        ).all()
        
        deactivated_count = 0
        for user in inactive_users:
            user.is_active = False
            deactivated_count += 1
        
        db.commit()
        print(f"Деактивировано {deactivated_count} неактивных пользователей")
        return {"deactivated_users": deactivated_count}
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при очистке пользователей: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def rotate_flags_task():
    """Периодическая смена флагов"""
    db = SessionLocal()
    
    try:
        from app.services.flag_service import FlagService
        
        flag_service = FlagService(db)
        flag_service.rotate_flags()
        
        print("Флаги успешно обновлены")
        return {"status": "success"}
        
    except Exception as e:
        print(f"Ошибка при смене флагов: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def backup_database_task():
    """Задача резервного копирования базы данных"""
    import subprocess
    import os
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/backups/ctf_backup_{timestamp}.sql"
        
        # Команда для создания бэкапа PostgreSQL
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "ctfuser", 
            "-d", "ctfarena",
            "-f", backup_file
        ]
        
        # Устанавливаем переменную окружения с паролем
        env = os.environ.copy()
        env["PGPASSWORD"] = "ctfpassword"
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Бэкап создан: {backup_file}")
            return {"status": "success", "file": backup_file}
        else:
            print(f"Ошибка создания бэкапа: {result.stderr}")
            return {"status": "error", "error": result.stderr}
            
    except Exception as e:
        print(f"Ошибка при создании бэкапа: {e}")
        return {"error": str(e)}