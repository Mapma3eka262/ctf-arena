# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BasePlugin(ABC):
    """Базовый класс для плагинов CTF-платформы"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Уникальное имя плагина"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Версия плагина"""
        pass
    
    @property
    def description(self) -> str:
        """Описание плагина"""
        return ""
    
    async def on_plugin_load(self):
        """Вызывается при загрузке плагина"""
        pass
    
    async def on_plugin_unload(self):
        """Вызывается при выгрузке плагина"""
        pass
    
    # Хуки для событий системы
    async def on_user_registration(self, user_data: Dict[str, Any]):
        """Вызывается при регистрации пользователя"""
        pass
    
    async def on_flag_submission(self, submission_data: Dict[str, Any]):
        """Вызывается при отправке флага"""
        pass
    
    async def on_challenge_solve(self, solve_data: Dict[str, Any]):
        """Вызывается при решении задания"""
        pass
    
    async def on_team_creation(self, team_data: Dict[str, Any]):
        """Вызывается при создании команды"""
        pass
    
    async def get_plugin_config(self) -> Dict[str, Any]:
        """Получение конфигурации плагина"""
        return {}
    
    async def set_plugin_config(self, config: Dict[str, Any]):
        """Установка конфигурации плагина"""
        pass