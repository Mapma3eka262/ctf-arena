from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models import Submission, Challenge, User, Team
from app.core.config import settings

class FlagService:
    
    @staticmethod
    def validate_flag_format(flag: str) -> bool:
        """Проверка формата флага"""
        return flag.startswith("CTF{") and flag.endswith("}")
    
    @staticmethod
    def submit_flag(db: Session, user_id: int, team_id: int, challenge_id: int, flag: str) -> dict:
        # Проверка формата флага
        if not FlagService.validate_flag_format(flag):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат флага. Должен быть CTF{...}"
            )
        
        # Проверка существования задания
        challenge = db.query(Challenge).filter(
            Challenge.id == challenge_id,
            Challenge.is_active == True
        ).first()
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задание не найдено или неактивно"
            )
        
        # Проверка, не отправлял ли уже пользователь этот флаг
        existing_submission = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.challenge_id == challenge_id,
            Submission.flag == flag
        ).first()
        
        if existing_submission:
            return {
                "status": existing_submission.status,
                "message": "Флаг уже был отправлен ранее",
                "points": existing_submission.points_awarded
            }
        
        # Проверка правильности флага
        is_correct = flag == challenge.flag
        
        # Проверка первого решения
        is_first_blood = False
        if is_correct:
            first_blood = db.query(Submission).filter(
                Submission.challenge_id == challenge_id,
                Submission.status == 'accepted'
            ).first()
            is_first_blood = not first_blood
        
        # Создание записи об отправке
        submission = Submission(
            user_id=user_id,
            team_id=team_id,
            challenge_id=challenge_id,
            flag=flag,
            status='accepted' if is_correct else 'rejected',
            submitted_at=datetime.utcnow(),
            points_awarded=challenge.points if is_correct else 0,
            is_first_blood=is_first_blood
        )
        
        db.add(submission)
        
        # Обновление счета команды
        if is_correct:
            team = db.query(Team).filter(Team.id == team_id).first()
            team.score += challenge.points
        
        db.commit()
        
        return {
            "status": submission.status,
            "message": "Правильный флаг!" if is_correct else "Неверный флаг",
            "points": submission.points_awarded,
            "is_first_blood": is_first_blood
        }
    
    @staticmethod
    def get_team_submissions(db: Session, team_id: int, limit: int = 50):
        return db.query(Submission).filter(
            Submission.team_id == team_id
        ).order_by(Submission.submitted_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_submission_stats(db: Session, team_id: int):
        submissions = db.query(Submission).filter(Submission.team_id == team_id).all()
        
        total = len(submissions)
        accepted = len([s for s in submissions if s.status == 'accepted'])
        rejected = len([s for s in submissions if s.status == 'rejected'])
        pending = len([s for s in submissions if s.status == 'pending'])
        
        return {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "success_rate": (accepted / total * 100) if total > 0 else 0
        }