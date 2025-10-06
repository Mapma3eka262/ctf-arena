from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Админская панель управления"""
    # Статистика системы
    total_users = db.query(User).count()
    total_teams = db.query(User).filter(User.team_id.isnot(None)).distinct(User.team_id).count()
    # Дополнительная статистика...
    
    return {
        "total_users": total_users,
        "total_teams": total_teams,
        "system_status": "online"
    }