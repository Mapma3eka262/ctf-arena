# backend/app/services/flag_service.py
from sqlalchemy.orm import Session
from app.models.challenge import Challenge
from app.core.security import validate_flag_format

class FlagService:
    def __init__(self, db: Session):
        self.db = db

    def verify_flag(self, challenge_id: int, submitted_flag: str) -> bool:
        """Проверка правильности флага"""
        if not validate_flag_format(submitted_flag):
            return False

        challenge = self.db.query(Challenge).filter(
            Challenge.id == challenge_id,
            Challenge.is_active == True
        ).first()

        if not challenge:
            return False

        # Простая проверка (в реальной системе может быть сложнее)
        return challenge.flag == submitted_flag

    def generate_flag(self, challenge_id: int) -> str:
        """Генерация флага для задания"""
        # В реальной системе здесь может быть сложная логика генерации
        import secrets
        import string
        
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        return f"CTF{{{random_part}}}"

    def rotate_flags(self):
        """Смена флагов для всех заданий"""
        challenges = self.db.query(Challenge).filter(Challenge.is_active == True).all()
        
        for challenge in challenges:
            new_flag = self.generate_flag(challenge.id)
            challenge.flag = new_flag
        
        self.db.commit()