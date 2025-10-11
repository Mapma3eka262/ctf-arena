# backend/app/core/microservices.py
from typing import Dict, Any, List
import asyncio
from abc import ABC, abstractmethod

class BaseMicroservice(ABC):
    """Базовый класс для микросервисов"""
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def shutdown(self):
        pass

class AuthService(BaseMicroservice):
    async def check_health(self) -> Dict[str, Any]:
        return {"status": "healthy", "service": "auth"}
    
    async def initialize(self):
        print("🛡️ Auth Service initialized")
    
    async def shutdown(self):
        print("🛡️ Auth Service shutdown")

class ScoringService(BaseMicroservice):
    async def check_health(self) -> Dict[str, Any]:
        return {"status": "healthy", "service": "scoring"}
    
    async def initialize(self):
        print("🏆 Scoring Service initialized")
    
    async def shutdown(self):
        print("🏆 Scoring Service shutdown")

class MicroserviceManager:
    def __init__(self):
        self.services: Dict[str, BaseMicroservice] = {}
    
    def register_service(self, name: str, service: BaseMicroservice):
        self.services[name] = service
    
    async def initialize(self):
        """Инициализация всех сервисов"""
        tasks = [service.initialize() for service in self.services.values()]
        await asyncio.gather(*tasks)
    
    async def shutdown(self):
        """Остановка всех сервисов"""
        tasks = [service.shutdown() for service in self.services.values()]
        await asyncio.gather(*tasks)
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """Проверка здоровья всех сервисов"""
        tasks = {name: service.check_health() for name, service in self.services.items()}
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results

# Глобальный экземпляр менеджера
microservice_manager = MicroserviceManager()