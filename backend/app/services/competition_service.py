from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Competition, Team

class CompetitionService:
    
    @staticmethod
    def get_current_competition(db: Session) -> Competition:
        """Получение текущего активного соревнования"""
        return db.query(Competition).filter(Competition.is_active == True).first()
    
    @staticmethod
    def extend_team_time(db: Session, team_id: int, penalty_minutes: int = None):
        """Продление времени команде с штрафом"""
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        competition = CompetitionService.get_current_competition(db)
        if not competition:
            raise HTTPException(status_code=400, detail="No active competition")
        
        # Используем штраф из настроек соревнования, если не указан
        penalty = penalty_minutes or competition.penalty_minutes
        
        # Увеличиваем штрафные минуты
        team.penalty_minutes += penalty
        
        # Устанавливаем время продления
        team.extended_until = datetime.utcnow() + timedelta(minutes=penalty)
        
        db.commit()
        
        return {
            "message": f"Team time extended with {penalty} minutes penalty",
            "penalty_minutes": team.penalty_minutes,
            "extended_until": team.extended_until
        }
    
    @staticmethod
    def get_competition_time_remaining(db: Session, team_id: int) -> dict:
        """Получение оставшегося времени для команды"""
        competition = CompetitionService.get_current_competition(db)
        if not competition:
            return {"active": False}
        
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return {"active": False}
        
        base_end_time = competition.end_time
        if team.extended_until and team.extended_until > base_end_time:
            end_time = team.extended_until
        else:
            end_time = base_end_time
        
        time_remaining = end_time - datetime.utcnow()
        
        return {
            "active": competition.is_active,
            "end_time": end_time,
            "time_remaining_seconds": max(0, int(time_remaining.total_seconds())),
            "has_penalty": team.penalty_minutes > 0,
            "penalty_minutes": team.penalty_minutes
        }
    
    @staticmethod
    def generate_competition_report(db: Session, competition_id: int) -> dict:
        """Генерация отчета по соревнованию"""
        competition = db.query(Competition).filter(Competition.id == competition_id).first()
        if not competition:
            raise HTTPException(status_code=404, detail="Competition not found")
        
        # Топ команд
        top_teams = db.query(Team).filter(Team.is_active == True).order_by(Team.score.desc()).limit(10).all()
        
        # Статистика по заданиям
        from app.models import Challenge, Submission
        challenges = db.query(Challenge).all()
        challenge_stats = []
        
        for challenge in challenges:
            total_submissions = db.query(Submission).filter(Submission.challenge_id == challenge.id).count()
            correct_submissions = db.query(Submission).filter(
                Submission.challenge_id == challenge.id,
                Submission.status == 'accepted'
            ).count()
            
            challenge_stats.append({
                "challenge_id": challenge.id,
                "title": challenge.title,
                "category": challenge.category,
                "points": challenge.points,
                "total_submissions": total_submissions,
                "correct_submissions": correct_submissions,
                "success_rate": (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
            })
        
        return {
            "competition": {
                "name": competition.name,
                "start_time": competition.start_time,
                "end_time": competition.end_time,
                "duration_hours": int((competition.end_time - competition.start_time).total_seconds() / 3600)
            },
            "top_teams": [
                {
                    "rank": i + 1,
                    "name": team.name,
                    "score": team.score,
                    "members_count": len(team.members)
                }
                for i, team in enumerate(top_teams)
            ],
            "challenge_stats": challenge_stats,
            "total_teams": db.query(Team).filter(Team.is_active == True).count(),
            "total_participants": db.query(User).filter(User.team_id.isnot(None)).count()
        }