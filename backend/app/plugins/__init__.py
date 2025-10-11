# backend/app/plugins/__init__.py
from typing import Dict, List, Any, Optional
import importlib
import pkgutil
import os

class PluginManager:
    """Менеджер плагинов для CTF-платформы"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.loaded_plugins: Dict[str, Any] = {}
    
    def discover_plugins(self, plugins_dir: str = "app/plugins"):
        """Обнаружение плагинов в директории"""
        plugin_modules = []
        
        for finder, name, ispkg in pkgutil.iter_modules([plugins_dir]):
            if name.startswith("plugin_") or name.endswith("_plugin"):
                try:
                    module = importlib.import_module(f"app.plugins.{name}")
                    plugin_modules.append(module)
                    print(f"🔍 Обнаружен плагин: {name}")
                except ImportError as e:
                    print(f"❌ Ошибка загрузки плагина {name}: {e}")
        
        return plugin_modules
    
    def load_plugin(self, plugin_class):
        """Загрузка конкретного плагина"""
        try:
            plugin_instance = plugin_class()
            self.loaded_plugins[plugin_instance.name] = plugin_instance
            await plugin_instance.on_plugin_load()
            print(f"✅ Плагин {plugin_instance.name} загружен")
            return plugin_instance
        except Exception as e:
            print(f"❌ Ошибка загрузки плагина {plugin_class.__name__}: {e}")
            return None
    
    def unload_plugin(self, plugin_name: str):
        """Выгрузка плагина"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            await plugin.on_plugin_unload()
            del self.loaded_plugins[plugin_name]
            print(f"✅ Плагин {plugin_name} выгружен")
    
    async def execute_hook(self, hook_name: str, *args, **kwargs):
        """Выполнение хука во всех загруженных плагинах"""
        for plugin_name, plugin in self.loaded_plugins.items():
            if hasattr(plugin, hook_name):
                try:
                    hook_method = getattr(plugin, hook_name)
                    if callable(hook_method):
                        await hook_method(*args, **kwargs)
                except Exception as e:
                    print(f"❌ Ошибка выполнения хука {hook_name} в плагине {plugin_name}: {e}")
    
    def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """Получение списка загруженных плагинов"""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in self.loaded_plugins.values()
        ]
    
    async def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Получение конфигурации плагина"""
        if plugin_name in self.loaded_plugins:
            return await self.loaded_plugins[plugin_name].get_plugin_config()
        return None
    
    async def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Установка конфигурации плагина"""
        if plugin_name in self.loaded_plugins:
            await self.loaded_plugins[plugin_name].set_plugin_config(config)

# Глобальный экземпляр менеджера плагинов
plugin_manager = PluginManager()