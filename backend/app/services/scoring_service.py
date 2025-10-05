from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Team, Submission, Challenge

class ScoringService:
    
    @staticmethod
    def calculate_team_score(db: Session, team_id: int) -> int:
        """Пересчет счета команды"""
        submissions = db.query(Submission).filter(
            Submission.team_id == team_id,
            Submission.status == 'accepted'
        ).all()
        
        total_score = sum(sub.points_awarded for sub in submissions)
        
        # Обновляем счет команды
        team = db.query(Team).filter(Team.id == team_id).first()
        if team:
            team.score = total_score
            db.commit()
        
        return total_score
    
    @staticmethod
    def award_first_blood_bonus(db: Session, submission_id: int):
        """Начисление бонуса за первую кровь"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission or not submission.is_first_blood:
            return
        
        # Бонус за первую кровь - 10% от стоимости задания
        challenge = submission.challenge
        bonus_points = int(challenge.points * 0.1)
        
        submission.points_awarded += bonus_points
        db.commit()
        
        # Обновляем общий счет команды
        ScoringService.calculate_team_score(db, submission.team_id)
    
    @staticmethod
    def get_team_solved_challenges(db: Session, team_id: int):
        """Получение решенных заданий команды"""
        submissions = db.query(Submission).filter(
            Submission.team_id == team_id,
            Submission.status == 'accepted'
        ).all()
        
        solved_challenges = set()
        for submission in submissions:
            solved_challenges.add(submission.challenge_id)
        
        return list(solved_challenges)
    
    @staticmethod
    def get_team_progress(db: Session, team_id: int):
        """Прогресс команды по категориям"""
        challenges_by_category = {}
        all_challenges = db.query(Challenge).filter(Challenge.is_active == True).all()
        
        for challenge in all_challenges:
            if challenge.category not in challenges_by_category:
                challenges_by_category[challenge.category] = {
                    'total': 0,
                    'solved': 0,
                    'total_points': 0,
                    'earned_points': 0
                }
            
            challenges_by_category[challenge.category]['total'] += 1
            challenges_by_category[challenge.category]['total_points'] += challenge.points
        
        # Подсчет решенных заданий
        solved_submissions = db.query(Submission).filter(
            Submission.team_id == team_id,
            Submission.status == 'accepted'
        ).all()
        
        for submission in solved_submissions:
            challenge = submission.challenge
            if challenge.category in challenges_by_category:
                challenges_by_category[challenge.category]['solved'] += 1
                challenges_by_category[challenge.category]['earned_points'] += submission.points_awarded
        
        return challenges_by_category