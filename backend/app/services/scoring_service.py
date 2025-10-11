# backend/app/services/scoring_service.py
from sqlalchemy.orm import Session
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.submission import Submission

class ScoringService:
    def __init__(self, db: Session):
        self.db = db

    def award_points(self, team_id: int, challenge_id: int, user_id: int) -> bool:
        """Начисление очков за решение задания"""
        challenge = self.db.query(Challenge).filter(Challenge.id == challenge_id).first()
        team = self.db.query(Team).filter(Team.id == team_id).first()
        
        if not challenge or not team:
            return False

        # Проверяем, первое ли это решение (First Blood)
        is_first_blood = self.db.query(Submission).filter(
            Submission.challenge_id == challenge_id,
            Submission.status == "accepted"
        ).count() == 0

        # Начисляем очки
        points = challenge.points
        team.score += points

        # Обновляем статистику задания
        challenge.solved_count += 1
        if is_first_blood:
            challenge.first_blood_user_id = user_id

        # Обновляем submission
        submission = self.db.query(Submission).filter(
            Submission.team_id == team_id,
            Submission.challenge_id == challenge_id,
            Submission.user_id == user_id
        ).order_by(Submission.submitted_at.desc()).first()

        if submission:
            submission.points_awarded = points
            submission.is_first_blood = is_first_blood

        self.db.commit()
        return is_first_blood

    def calculate_dynamic_score(self, challenge: Challenge) -> int:
        """Расчет динамических очков для задания"""
        base_points = challenge.points
        solved_count = challenge.solved_count
        
        # Формула для динамических очков
        if solved_count == 0:
            return base_points
        else:
            # Очки уменьшаются с количеством решений
            min_points = base_points * 0.3
            decay = 0.05  # Коэффициент затухания
            dynamic_points = min_points + (base_points - min_points) * (0.95 ** solved_count)
            return int(dynamic_points)

    def get_team_rank(self, team_id: int) -> int:
        """Получение позиции команды в рейтинге"""
        teams = self.db.query(Team).order_by(Team.score.desc()).all()
        for index, team in enumerate(teams, 1):
            if team.id == team_id:
                return index
        return 0