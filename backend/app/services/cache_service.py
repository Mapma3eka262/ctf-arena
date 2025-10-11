# backend/app/services/cache_service.py
from typing import Any, Optional
from app.core.cache import cache_manager

class CacheService:
    """Сервис для работы с кэшем"""
    
    def __init__(self):
        self.cache = cache_manager
    
    def get_challenge(self, challenge_id: int) -> Optional[dict]:
        """Получение задания из кэша"""
        return self.cache.get(f"challenge:{challenge_id}")
    
    def set_challenge(self, challenge_id: int, challenge_data: dict, expire: int = 300):
        """Сохранение задания в кэш"""
        return self.cache.set(f"challenge:{challenge_id}", challenge_data, expire)
    
    def get_team_stats(self, team_id: int) -> Optional[dict]:
        """Получение статистики команды из кэша"""
        return self.cache.get(f"team_stats:{team_id}")
    
    def set_team_stats(self, team_id: int, stats: dict, expire: int = 60):
        """Сохранение статистики команды в кэш"""
        return self.cache.set(f"team_stats:{team_id}", stats, expire)
    
    def invalidate_challenge(self, challenge_id: int):
        """Инвалидация кэша задания"""
        self.cache.delete(f"challenge:{challenge_id}")
    
    def invalidate_team_stats(self, team_id: int):
        """Инвалидация кэша статистики команды"""
        self.cache.delete(f"team_stats:{team_id}")
    
    def get_leaderboard(self) -> Optional[list]:
        """Получение таблицы лидеров из кэша"""
        return self.cache.get("leaderboard")
    
    def set_leaderboard(self, leaderboard: list, expire: int = 30):
        """Сохранение таблицы лидеров в кэш"""
        return self.cache.set("leaderboard", leaderboard, expire)