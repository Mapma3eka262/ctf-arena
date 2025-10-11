# backend/app/core/auth.py (дополнение)
from fastapi import WebSocket, Query, Cookie
from jose import JWTError, jwt
from app.core.config import settings

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