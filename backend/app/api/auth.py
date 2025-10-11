# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.auth import get_current_user
from app.schemas.auth import UserRegister, Token
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.tasks.email_tasks import send_confirmation_email_task

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя и создание команды"""
    auth_service = AuthService(db)
    
    # Проверка существования пользователя
    if auth_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
    
    if auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создание пользователя и команды
    user = auth_service.create_user_and_team(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        team_name=user_data.team_name
    )
    
    # Логирование события
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="user_registration",
        resource_type="user",
        user_id=user.id,
        details={"username": user.username, "team_name": user_data.team_name}
    )
    
    # Отправка email подтверждения (асинхронно)
    send_confirmation_email_task.delay(user.email, user.username)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    auth_service = AuthService(db)
    audit_service = AuditService(db)
    
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        # Логирование неудачной попытки входа
        await audit_service.log_user_login(
            user_id=0,  # Неизвестный пользователь
            ip_address="127.0.0.1",  # В реальном приложении получить из запроса
            user_agent="unknown",
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создание токенов
    access_token_expires = timedelta(minutes=60 * 24)  # 24 часа
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Обновление времени последнего входа
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Логирование успешного входа
    await audit_service.log_user_login(
        user_id=user.id,
        ip_address="127.0.0.1",  # В реальном приложении получить из запроса
        user_agent="unknown", 
        status="success"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": access_token,  # В реальном приложении отдельный refresh token
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user

@router.post("/refresh")
async def refresh_token(
    current_user: UserResponse = Depends(get_current_user)
):
    """Обновление access token"""
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Выход пользователя (в JWT это в основном клиентская операция)"""
    audit_service = AuditService(db)
    await audit_service.log_event(
        action="user_logout",
        resource_type="user", 
        user_id=current_user.id,
        details={"username": current_user.username}
    )
    
    return {"message": "Успешный выход из системы"}