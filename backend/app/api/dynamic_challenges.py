# backend/app/api/dynamic_challenges.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.dynamic_service import DynamicChallengeService

router = APIRouter()

@router.post("/{challenge_id}/instance")
async def create_challenge_instance(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание инстанса динамического задания"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не состоит в команде"
        )
    
    dynamic_service = DynamicChallengeService(db)
    
    # Проверяем, не создан ли уже инстанс для этой команды
    from app.models.dynamic_challenge import ChallengeInstance
    existing_instance = db.query(ChallengeInstance).filter(
        ChallengeInstance.dynamic_challenge_id == challenge_id,
        ChallengeInstance.team_id == current_user.team.id,
        ChallengeInstance.status == "running"
    ).first()
    
    if existing_instance:
        return {
            "instance_id": existing_instance.id,
            "host": "localhost",
            "port": existing_instance.host_port,
            "status": existing_instance.status,
            "expires_at": existing_instance.expires_at.isoformat()
        }
    
    # Создаем новый инстанс
    instance = await dynamic_service.create_instance(challenge_id, current_user.team.id)
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать инстанс задания"
        )
    
    return instance

@router.delete("/instance/{instance_id}")
async def destroy_challenge_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Уничтожение инстанса задания"""
    dynamic_service = DynamicChallengeService(db)
    
    # Проверяем права доступа
    from app.models.dynamic_challenge import ChallengeInstance
    instance = db.query(ChallengeInstance).filter(
        ChallengeInstance.id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Инстанс не найден"
        )
    
    if instance.team_id != current_user.team.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для управления этим инстансом"
        )
    
    success = await dynamic_service.destroy_instance(instance_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось уничтожить инстанс"
        )
    
    return {"message": "Инстанс успешно уничтожен"}

@router.get("/team/instances")
async def get_team_instances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех инстансов команды"""
    if not current_user.team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не состоит в команде"
        )
    
    from app.models.dynamic_challenge import ChallengeInstance
    instances = db.query(ChallengeInstance).filter(
        ChallengeInstance.team_id == current_user.team.id
    ).all()
    
    return [
        {
            "id": instance.id,
            "challenge_id": instance.dynamic_challenge_id,
            "status": instance.status,
            "host": "localhost",
            "port": instance.host_port,
            "created_at": instance.created_at.isoformat(),
            "expires_at": instance.expires_at.isoformat() if instance.expires_at else None
        }
        for instance in instances
    ]