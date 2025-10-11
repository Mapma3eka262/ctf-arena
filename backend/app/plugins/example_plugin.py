from typing import Dict, Any

class ExamplePlugin:
    """Пример плагина для CTF-платформы"""
    
    def __init__(self):
        self.name = "example_plugin"
        self.version = "1.0.0"
        self.description = "Пример плагина для демонстрации"
    
    async def on_plugin_load(self):
        """Вызывается при загрузке плагина"""
        print(f"🎯 Плагин {self.name} v{self.version} загружен")
    
    async def on_plugin_unload(self):
        """Вызывается при выгрузке плагина"""
        print(f"🎯 Плагин {self.name} выгружен")
    
    async def get_plugin_config(self) -> Dict[str, Any]:
        """Получение конфигурации плагина"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }
    
    async def set_plugin_config(self, config: Dict[str, Any]):
        """Установка конфигурации плагина"""
        pass
    
    # Пример хуков
    async def on_flag_submission(self, user_id: int, challenge_id: int, result: bool):
        """Хук для обработки отправки флага"""
        if result:
            print(f"🎉 Пользователь {user_id} решил задание {challenge_id}")
