from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.models import User, Team
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register_user(db, request)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    return AuthService.verify_email(db, token)

@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    return AuthService.refresh_token(db, refresh_token)

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    return AuthService.forgot_password(db, email)

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    return AuthService.reset_password(db, token, new_password)