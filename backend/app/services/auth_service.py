from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import secrets
import bcrypt

from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from app.core.config import settings
from app.models import User, Team
from app.schemas.auth import RegisterRequest, TokenResponse

class AuthService:
    
    @staticmethod
    def register_user(db: Session, request: RegisterRequest) -> TokenResponse:
        # Проверка существования пользователя
        if db.query(User).filter(User.username == request.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует"
            )
        
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Проверка существования команды
        if db.query(Team).filter(Team.name == request.team_name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Команда с таким названием уже существует"
            )
        
        try:
            # Создание команды
            team = Team(
                name=request.team_name,
                registration_date=datetime.utcnow(),
                is_active=True
            )
            db.add(team)
            db.flush()  # Получаем ID команды
            
            # Создание пользователя (капитана)
            user = User(
                username=request.username,
                email=request.email,
                password_hash=get_password_hash(request.password),
                role='captain',
                team_id=team.id,
                language=settings.DEFAULT_LANGUAGE,
                is_active=True,
                email_verified=False
            )
            db.add(user)
            db.flush()
            
            # Обновляем captain_id в команде
            team.captain_id = user.id
            db.commit()
            
            # Создание токенов
            access_token = create_access_token(data={"sub": user.username})
            refresh_token = create_refresh_token(data={"sub": user.username})
            
            # TODO: Отправка email для верификации
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                team_id=team.id,
                role=user.role
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при создании пользователя"
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь деактивирован"
            )
        return user
    
    @staticmethod
    def verify_email(db: Session, token: str) -> dict:
        # TODO: Реализация верификации email
        return {"message": "Email verified successfully"}
    
    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> TokenResponse:
        # TODO: Реализация обновления токена
        pass
    
    @staticmethod
    def forgot_password(db: Session, email: str) -> dict:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Для безопасности не сообщаем, что email не существует
            return {"message": "Если email существует, инструкции отправлены"}
        
        # TODO: Генерация токена сброса и отправка email
        return {"message": "Если email существует, инструкции отправлены"}
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict:
        # TODO: Валидация токена и сброс пароля
        return {"message": "Пароль успешно изменен"}