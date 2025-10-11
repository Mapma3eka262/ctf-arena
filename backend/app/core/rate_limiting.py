# backend/app/core/rate_limiting.py
import time
from typing import Optional
from fastapi import HTTPException, status
from app.core.cache import cache_manager

class RateLimiter:
    """Система ограничения запросов"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    async def is_rate_limited(self, 
                            identifier: str, 
                            limit: int, 
                            window: int,
                            action: str = "request") -> bool:
        """
        Проверка превышения лимита запросов
        
        Args:
            identifier: Уникальный идентификатор (user_id, ip, etc)
            limit: Максимальное количество запросов
            window: Временное окно в секундах
            action: Тип действия для дифференциации лимитов
        """
        key = f"rate_limit:{action}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window
        
        try:
            # Получаем историю запросов
            requests = self.cache.get(key) or []
            
            # Удаляем старые запросы вне временного окна
            requests = [req_time for req_time in requests if req_time > window_start]
            
            # Проверяем лимит
            if len(requests) >= limit:
                return True
            
            # Добавляем текущий запрос
            requests.append(current_time)
            self.cache.set(key, requests, window)
            
            return False
            
        except Exception as e:
            print(f"Rate limit error: {e}")
            return False
    
    async def get_remaining_requests(self, 
                                   identifier: str, 
                                   limit: int, 
                                   window: int,
                                   action: str = "request") -> int:
        """Получение количества оставшихся запросов"""
        key = f"rate_limit:{action}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window
        
        try:
            requests = self.cache.get(key) or []
            requests = [req_time for req_time in requests if req_time > window_start]
            
            return max(0, limit - len(requests))
            
        except:
            return limit

# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter(cache_manager)

def rate_limit(limit: int = 60, window: int = 60, action: str = "request"):
    """Декоратор для ограничения запросов к endpoint"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            # Используем IP адрес как идентификатор
            identifier = request.client.host
            
            if await rate_limiter.is_rate_limited(identifier, limit, window, action):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {window} seconds."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator