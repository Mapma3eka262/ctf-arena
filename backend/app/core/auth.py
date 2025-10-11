# backend/app/core/auth.py (дополнение)
backend/app/core/auth.py        # Аутентификация
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi import WebSocket, Query, Cookie
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из JWT токена"""
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь неактивен"
        )
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка прав администратора"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user

async def get_team_captain(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка прав капитана команды"""
    if not current_user.is_captain:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только капитан команды может выполнять это действие"
        )
    return current_user

async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(None),
    session: str = Cookie(None)
) -> dict:
    """Аутентификация пользователя для WebSocket соединения"""
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                await websocket.close(code=1008)
                raise credentials_exception
        except JWTError:
            await websocket.close(code=1008)
            raise credentials_exception
        
        # Получаем пользователя из базы данных
        from app.core.database import get_db
        from app.models.user import User
        
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        
        if user is None or not user.is_active:
            await websocket.close(code=1008)
            raise credentials_exception
        
        return {
            "user_id": user.id,
            "username": user.username,
            "team_id": user.team_id,
            "is_admin": user.is_admin
        }
    
    await websocket.close(code=1008)
    return {}
