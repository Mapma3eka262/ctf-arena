# backend/app/utils/docker_manager.py
import docker
import asyncio
from typing import Dict, List, Optional
from docker.models.containers import Container

class DockerManager:
    """Менеджер для работы с Docker"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "ctf_network"
        self._ensure_network()
    
    def _ensure_network(self):
        """Создание сети Docker если не существует"""
        try:
            self.client.networks.get(self.network_name)
        except docker.errors.NotFound:
            print(f"🌐 Создание сети Docker: {self.network_name}")
            self.client.networks.create(
                self.network_name,
                driver="bridge",
                check_duplicate=True
            )
    
    async def create_container(self, 
                             image: str,
                             environment: Dict[str, str],
                             ports: Dict[str, int],
                             resource_limits: Dict[str, str] = None) -> Optional[Container]:
        """Создание Docker контейнера"""
        try:
            container_config = {
                'image': image,
                'environment': environment,
                'ports': ports,
                'network': self.network_name,
                'detach': True,
                'auto_remove': True
            }
            
            if resource_limits:
                container_config['mem_limit'] = resource_limits.get('memory', '100m')
                container_config['cpu_shares'] = resource_limits.get('cpu', 1024)
            
            container = self.client.containers.run(**container_config)
            return container
            
        except Exception as e:
            print(f"❌ Ошибка создания контейнера: {e}")
            return None
    
    async def stop_container(self, container_id: str) -> bool:
        """Остановка контейнера"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            print(f"❌ Ошибка остановки контейнера {container_id}: {e}")
            return False
    
    async def get_container_status(self, container_id: str) -> Optional[Dict[str, str]]:
        """Получение статуса контейнера"""
        try:
            container = self.client.containers.get(container_id)
            return {
                'id': container.id,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'created': container.attrs['Created'],
                'ports': container.ports
            }
        except Exception as e:
            print(f"❌ Ошибка получения статуса контейнера {container_id}: {e}")
            return None
    
    async def list_containers(self, filters: Dict = None) -> List[Dict]:
        """Список всех контейнеров"""
        try:
            containers = self.client.containers.list(all=True, filters=filters)
            return [
                {
                    'id': container.id,
                    'name': container.name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else 'unknown'
                }
                for container in containers
            ]
        except Exception as e:
            print(f"❌ Ошибка получения списка контейнеров: {e}")
            return []
    
    async def cleanup_orphaned_containers(self):
        """Очистка зависших контейнеров"""
        try:
            # Находим контейнеры которые завершились с ошибкой
            filters = {'status': 'exited'}
            exited_containers = self.client.containers.list(all=True, filters=filters)
            
            for container in exited_containers:
                try:
                    container.remove()
                    print(f"🧹 Удален контейнер: {container.id}")
                except Exception as e:
                    print(f"❌ Ошибка удаления контейнера {container.id}: {e}")
                    
        except Exception as e:
            print(f"❌ Ошибка очистки контейнеров: {e}")