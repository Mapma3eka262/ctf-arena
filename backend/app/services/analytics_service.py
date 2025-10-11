# backend/app/services/analytics_service.py
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

class AnalyticsService:
    """Сервис для расширенной аналитики и статистики"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_team_insights(self, team_id: int) -> Dict[str, Any]:
        """Получение аналитических данных по команде"""
        return {
            'strengths': await self.analyze_strengths(team_id),
            'weaknesses': await self.analyze_weaknesses(team_id),
            'recommendations': await self.generate_recommendations(team_id),
            'comparison': await self.compare_with_top_teams(team_id),
            'activity_patterns': await self.analyze_activity_patterns(team_id)
        }
    
    async def analyze_strengths(self, team_id: int) -> List[Dict[str, Any]]:
        """Анализ сильных сторон команды"""
        from app.models.submission import Submission
        from app.models.challenge import Challenge
        
        # Анализ успешных решений по категориям
        strengths = self.db.query(
            Challenge.category,
            func.count(Submission.id).label('solved_count'),
            func.avg(Challenge.points).label('avg_points')
        ).join(
            Submission, 
            and_(
                Submission.challenge_id == Challenge.id,
                Submission.team_id == team_id,
                Submission.status == 'accepted'
            )
        ).group_by(Challenge.category).all()
        
        return [
            {
                'category': strength.category,
                'solved_count': strength.solved_count,
                'avg_points': float(strength.avg_points or 0),
                'strength_score': strength.solved_count * float(strength.avg_points or 0)
            }
            for strength in strengths
            if strength.solved_count > 0
        ]
    
    async def analyze_weaknesses(self, team_id: int) -> List[Dict[str, Any]]:
        """Анализ слабых сторон команды"""
        from app.models.submission import Submission
        from app.models.challenge import Challenge
        
        # Все доступные категории
        all_categories = self.db.query(Challenge.category).distinct().all()
        all_categories = [cat[0] for cat in all_categories]
        
        # Решенные категории
        solved_categories = self.db.query(Challenge.category).join(
            Submission, 
            and_(
                Submission.challenge_id == Challenge.id,
                Submission.team_id == team_id,
                Submission.status == 'accepted'
            )
        ).distinct().all()
        solved_categories = [cat[0] for cat in solved_categories]
        
        # Не решенные категории
        unsolved_categories = list(set(all_categories) - set(solved_categories))
        
        # Категории с низким процентом успеха
        weak_categories = self.db.query(
            Challenge.category,
            func.count(Submission.id).label('total_attempts'),
            func.sum(
                func.case((Submission.status == 'accepted', 1), else_=0)
            ).label('successful_attempts')
        ).join(
            Submission, 
            and_(
                Submission.challenge_id == Challenge.id,
                Submission.team_id == team_id
            )
        ).group_by(Challenge.category).having(
            func.count(Submission.id) > 2  # Минимум 3 попытки
        ).all()
        
        weaknesses = []
        for category in unsolved_categories:
            weaknesses.append({
                'category': category,
                'reason': 'no_attempts',
                'priority': 'high'
            })
        
        for weak in weak_categories:
            success_rate = (weak.successful_attempts or 0) / weak.total_attempts
            if success_rate < 0.3:  # Меньше 30% успеха
                weaknesses.append({
                    'category': weak.category,
                    'reason': 'low_success_rate',
                    'success_rate': success_rate,
                    'total_attempts': weak.total_attempts,
                    'priority': 'medium' if success_rate > 0.1 else 'high'
                })
        
        return weaknesses
    
    async def generate_recommendations(self, team_id: int) -> List[Dict[str, Any]]:
        """Генерация рекомендаций для команды"""
        weaknesses = await self.analyze_weaknesses(team_id)
        strengths = await self.analyze_strengths(team_id)
        
        recommendations = []
        
        for weakness in weaknesses:
            if weakness['reason'] == 'no_attempts':
                recommendations.append({
                    'type': 'explore_category',
                    'category': weakness['category'],
                    'priority': weakness['priority'],
                    'message': f'Попробуйте задания в категории {weakness["category"]}',
                    'action': 'view_challenges'
                })
            elif weakness['reason'] == 'low_success_rate':
                recommendations.append({
                    'type': 'improve_skills',
                    'category': weakness['category'],
                    'priority': weakness['priority'],
                    'message': f'Улучшите навыки в {weakness["category"]} (успешность: {weakness["success_rate"]:.1%})',
                    'action': 'practice_category'
                })
        
        # Рекомендации на основе сильных сторон
        if strengths:
            best_category = max(strengths, key=lambda x: x['strength_score'])
            recommendations.append({
                'type': 'leverage_strength',
                'category': best_category['category'],
                'priority': 'low',
                'message': f'Используйте вашу силу в {best_category["category"]} для решения сложных заданий',
                'action': 'advanced_challenges'
            })
        
        return recommendations
    
    async def compare_with_top_teams(self, team_id: int) -> Dict[str, Any]:
        """Сравнение команды с топовыми командами"""
        from app.models.team import Team
        from app.models.submission import Submission
        
        # Текущая позиция команды
        current_team = self.db.query(Team).filter(Team.id == team_id).first()
        if not current_team:
            return {}
        
        # Топ 5 команд
        top_teams = self.db.query(Team).order_by(desc(Team.score)).limit(5).all()
        
        # Статистика текущей команды
        team_stats = self.db.query(
            func.count(Submission.id).label('total_submissions'),
            func.sum(
                func.case((Submission.status == 'accepted', 1), else_=0)
            ).label('accepted_submissions')
        ).filter(Submission.team_id == team_id).first()
        
        # Статистика топ команд
        top_teams_stats = []
        for team in top_teams:
            stats = self.db.query(
                func.count(Submission.id).label('total_submissions'),
                func.sum(
                    func.case((Submission.status == 'accepted', 1), else_=0)
                ).label('accepted_submissions')
            ).filter(Submission.team_id == team.id).first()
            
            top_teams_stats.append({
                'team_name': team.name,
                'score': team.score,
                'total_submissions': stats.total_submissions or 0,
                'accepted_submissions': stats.accepted_submissions or 0,
                'success_rate': (stats.accepted_submissions or 0) / (stats.total_submissions or 1)
            })
        
        return {
            'current_team': {
                'score': current_team.score,
                'total_submissions': team_stats.total_submissions or 0,
                'accepted_submissions': team_stats.accepted_submissions or 0,
                'success_rate': (team_stats.accepted_submissions or 0) / (team_stats.total_submissions or 1)
            },
            'top_teams': top_teams_stats,
            'score_gap': top_teams[0].score - current_team.score if top_teams else 0
        }
    
    async def analyze_activity_patterns(self, team_id: int) -> Dict[str, Any]:
        """Анализ паттернов активности команды"""
        from app.models.submission import Submission
        
        # Активность по часам
        hourly_activity = self.db.query(
            func.extract('hour', Submission.submitted_at).label('hour'),
            func.count(Submission.id).label('submission_count')
        ).filter(
            Submission.team_id == team_id,
            Submission.submitted_at >= datetime.utcnow() - timedelta(days=7)
        ).group_by('hour').all()
        
        # Активность по дням недели
        daily_activity = self.db.query(
            func.extract('dow', Submission.submitted_at).label('day_of_week'),
            func.count(Submission.id).label('submission_count')
        ).filter(
            Submission.team_id == team_id,
            Submission.submitted_at >= datetime.utcnow() - timedelta(days=30)
        ).group_by('day_of_week').all()
        
        return {
            'hourly_activity': [
                {'hour': int(act.hour), 'submissions': act.submission_count}
                for act in hourly_activity
            ],
            'daily_activity': [
                {'day': int(act.day_of_week), 'submissions': act.submission_count}
                for act in daily_activity
            ],
            'most_active_hour': max(hourly_activity, key=lambda x: x.submission_count).hour if hourly_activity else None,
            'most_active_day': max(daily_activity, key=lambda x: x.submission_count).day_of_week if daily_activity else None
        }
    
    async def get_global_statistics(self) -> Dict[str, Any]:
        """Глобальная статистика платформы"""
        from app.models.user import User
        from app.models.team import Team
        from app.models.challenge import Challenge
        from app.models.submission import Submission
        
        total_users = self.db.query(User).count()
        total_teams = self.db.query(Team).count()
        total_challenges = self.db.query(Challenge).filter(Challenge.is_active == True).count()
        total_submissions = self.db.query(Submission).count()
        
        # Самые популярные категории
        popular_categories = self.db.query(
            Challenge.category,
            func.count(Submission.id).label('submission_count'),
            func.count(func.distinct(Submission.team_id)).label('team_count')
        ).join(Submission).group_by(Challenge.category).order_by(desc('submission_count')).limit(5).all()
        
        # Самые сложные задания
        hardest_challenges = self.db.query(
            Challenge.title,
            Challenge.category,
            Challenge.points,
            func.count(Submission.id).label('total_attempts'),
            func.sum(
                func.case((Submission.status == 'accepted', 1), else_=0)
            ).label('successful_attempts')
        ).join(Submission).group_by(
            Challenge.id, Challenge.title, Challenge.category, Challenge.points
        ).having(
            func.count(Submission.id) >= 5  # Минимум 5 попыток
        ).order_by(
            (func.sum(func.case((Submission.status == 'accepted', 1), else_=0)) / func.count(Submission.id)).asc()
        ).limit(5).all()
        
        return {
            'total_users': total_users,
            'total_teams': total_teams,
            'total_challenges': total_challenges,
            'total_submissions': total_submissions,
            'popular_categories': [
                {
                    'category': cat.category,
                    'submission_count': cat.submission_count,
                    'team_count': cat.team_count
                }
                for cat in popular_categories
            ],
            'hardest_challenges': [
                {
                    'title': chal.title,
                    'category': chal.category,
                    'points': chal.points,
                    'success_rate': (chal.successful_attempts or 0) / (chal.total_attempts or 1),
                    'total_attempts': chal.total_attempts
                }
                for chal in hardest_challenges
            ]
        }