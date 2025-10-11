# backend/app/core/cache.py
import redis
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
from app.core.config import settings

class CacheManager:
    """Менеджер кэширования на основе Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except:
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Установка значения в кэш"""
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, expire, serialized_value)
        except:
            return False
    
    def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        try:
            return bool(self.redis_client.delete(key))
        except:
            return False
    
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            return bool(self.redis_client.exists(key))
        except:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистка ключей по шаблону"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except:
            return 0

# Глобальный экземпляр кэш-менеджера
cache_manager = CacheManager()

def cached(key_pattern: str, expire: int = 3600):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерация ключа кэша
            cache_key = key_pattern.format(*args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию и сохраняем результат
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(key_pattern: str):
    """Декоратор для инвалидации кэша"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Инвалидируем кэш после выполнения функции
            cache_key = key_pattern.format(*args, **kwargs)
            cache_manager.delete(cache_key)
            
            return result
        return wrapper
    return decorator