from sqlalchemy.orm import Session
from app.models.user import User
from app.models.team import Team
from app.core.security import verify_password, get_password_hash

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> User:
        """Аутентификация пользователя"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_username(self, username: str) -> User:
        """Получение пользователя по логину"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_user_and_team(self, username: str, email: str, password: str, team_name: str) -> User:
        """Создание пользователя и команды"""
        # Создание команды
        team = Team(name=team_name)
        self.db.add(team)
        self.db.flush()  # Получаем ID команды

        # Создание пользователя (капитана)
        user = User(
            username=username,
            email=email,
            is_captain=True
        )
        user.set_password(password)
        user.team_id = team.id
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def activate_user(self, user_id: int) -> bool:
        """Активация пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = True
            self.db.commit()
            return True
        return False