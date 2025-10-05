from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Team, Challenge, Competition, Service
from app.services.monitoring_service import MonitoringService

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    """Проверка прав администратора"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Данные для админ панели"""
    # Статистика команд
    teams_count = db.query(Team).count()
    active_teams = db.query(Team).filter(Team.is_active == True).count()
    
    # Статистика пользователей
    users_count = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Статистика заданий
    challenges_count = db.query(Challenge).count()
    active_challenges = db.query(Challenge).filter(Challenge.is_active == True).count()
    
    # Статистика сервисов
    services_health = MonitoringService.get_services_health_summary(db)
    
    # Активное соревнование
    current_competition = db.query(Competition).filter(Competition.is_active == True).first()
    
    return {
        "teams": {
            "total": teams_count,
            "active": active_teams
        },
        "users": {
            "total": users_count,
            "active": active_users
        },
        "challenges": {
            "total": challenges_count,
            "active": active_challenges
        },
        "services_health": services_health,
        "current_competition": current_competition.name if current_competition else None
    }

@router.post("/teams")
async def create_team(
    name: str,
    captain_username: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Создание команды администратором"""
    # Проверка существования команды
    if db.query(Team).filter(Team.name == name).first():
        raise HTTPException(status_code=400, detail="Team already exists")
    
    # Поиск пользователя для назначения капитаном
    captain = db.query(User).filter(User.username == captain_username).first()
    if not captain:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Создание команды
    team = Team(
        name=name,
        captain_id=captain.id,
        registration_date=datetime.utcnow(),
        is_active=True
    )
    db.add(team)
    db.commit()
    
    # Обновление роли пользователя
    captain.role = 'captain'
    captain.team_id = team.id
    db.commit()
    
    return {"message": "Team created successfully", "team_id": team.id}

@router.post("/challenges")
async def create_challenge(
    title: str,
    category: str,
    points: int,
    description: str,
    flag: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Создание задания"""
    challenge = Challenge(
        title=title,
        category=category,
        points=points,
        description=description,
        flag=flag,
        is_active=True
    )
    db.add(challenge)
    db.commit()
    
    return {"message": "Challenge created successfully", "challenge_id": challenge.id}

@router.post("/competition/start")
async def start_competition(
    name: str,
    duration_hours: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Начало соревнования"""
    # Завершаем предыдущие активные соревнования
    db.query(Competition).filter(Competition.is_active == True).update({"is_active": False})
    
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=duration_hours)
    
    competition = Competition(
        name=name,
        start_time=start_time,
        end_time=end_time,
        is_active=True
    )
    db.add(competition)
    db.commit()
    
    return {
        "message": "Competition started",
        "start_time": start_time,
        "end_time": end_time
    }

@router.post("/competition/stop")
async def stop_competition(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Остановка соревнования"""
    competition = db.query(Competition).filter(Competition.is_active == True).first()
    if not competition:
        raise HTTPException(status_code=404, detail="No active competition found")
    
    competition.is_active = False
    competition.end_time = datetime.utcnow()
    db.commit()
    
    return {"message": "Competition stopped"}

@router.get("/services")
async def get_all_services(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Статус всех сервисов"""
    services = db.query(Service).all()
    
    return [
        {
            "id": service.id,
            "name": service.name,
            "type": service.type,
            "team_id": service.team_id,
            "team_name": service.team.name if service.team else "No team",
            "status": service.status,
            "last_checked": service.last_checked
        }
        for service in services
    ]

@router.post("/services/{service_id}/restart")
async def restart_service(
    service_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Перезапуск сервиса"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Здесь должна быть логика перезапуска сервиса
    # Например, через Docker API или SSH
    
    return {"message": f"Service {service.name} restart initiated"}