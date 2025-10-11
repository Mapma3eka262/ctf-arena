# backend/app/services/competition_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.competition import Competition

class CompetitionService:
    def __init__(self, db: Session):
        self.db = db

    def get_current_competition(self) -> Competition:
        """Получение текущего активного соревнования"""
        now = datetime.utcnow()
        return self.db.query(Competition).filter(
            Competition.is_active == True,
            Competition.start_time <= now,
            Competition.end_time >= now
        ).first()

    def start_competition(self, competition_id: int) -> bool:
        """Запуск соревнования"""
        competition = self.db.query(Competition).filter(Competition.id == competition_id).first()
        if competition:
            competition.is_active = True
            self.db.commit()
            return True
        return False

    def stop_competition(self, competition_id: int) -> bool:
        """Остановка соревнования"""
        competition = self.db.query(Competition).filter(Competition.id == competition_id).first()
        if competition:
            competition.is_active = False
            self.db.commit()
            return True
        return False

    def get_competition_time_remaining(self, competition_id: int) -> int:
        """Получение оставшегося времени соревнования в секундах"""
        competition = self.db.query(Competition).filter(Competition.id == competition_id).first()
        if not competition or not competition.is_running():
            return 0
        
        now = datetime.utcnow()
        remaining = competition.end_time - now
        return max(0, int(remaining.total_seconds()))

    def get_leaderboard(self, competition_id: int, limit: int = 10):
        """Получение таблицы лидеров для соревнования"""
        from app.models.team import Team
        from app.models.submission import Submission
        
        # В реальной системе здесь будет сложный запрос
        # для подсчета очков только за текущее соревнование
        teams = self.db.query(Team).order_by(Team.score.desc()).limit(limit).all()
        
        return [
            {
                "position": idx + 1,
                "team_name": team.name,
                "score": team.score,
                "country": team.country
            }
            for idx, team in enumerate(teams)
        ]