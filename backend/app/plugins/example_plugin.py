# backend/app/plugins/example_plugin.py
from .base import BasePlugin
from typing import Dict, Any
import requests

class ExampleNotificationPlugin(BasePlugin):
    """Пример плагина для расширенных уведомлений"""
    
    @property
    def name(self) -> str:
        return "example_notifications"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Плагин для отправки уведомлений в внешние системы"
    
    def __init__(self):
        self.webhook_url = None
        self.enabled = False
    
    async def on_plugin_load(self):
        print(f"🔌 Плагин {self.name} загружен")
    
    async def on_flag_submission(self, submission_data: Dict[str, Any]):
        if not self.enabled or not self.webhook_url:
            return
        
        # Отправка уведомления в внешнюю систему
        payload = {
            "event": "flag_submission",
            "data": submission_data,
            "timestamp": submission_data.get('timestamp')
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Уведомление отправлено в {self.webhook_url}")
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
    
    async def on_challenge_solve(self, solve_data: Dict[str, Any]):
        if not self.enabled or not self.webhook_url:
            return
        
        # Отправка уведомления о решении задания
        payload = {
            "event": "challenge_solve",
            "data": solve_data,
            "timestamp": solve_data.get('timestamp')
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Уведомление о решении отправлено")
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
    
    async def get_plugin_config(self) -> Dict[str, Any]:
        return {
            "webhook_url": self.webhook_url,
            "enabled": self.enabled
        }
    
    async def set_plugin_config(self, config: Dict[str, Any]):
        self.webhook_url = config.get("webhook_url")
        self.enabled = config.get("enabled", False)