# backend/app/utils/deployment.py
import docker
import yaml
import asyncio
from typing import Dict, Any, List
from pathlib import Path

class ChallengeDeployer:
    """Утилита для развертывания динамических заданий"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.challenges_dir = Path("challenges")
    
    async def deploy_challenge(self, challenge_config: Dict[str, Any]) -> bool:
        """Развертывание задания из конфигурации"""
        try:
            # Создание Dockerfile если нужно
            if challenge_config.get('build_context'):
                await self.build_image(challenge_config)
            
            # Запуск контейнера
            container = await self.create_container(challenge_config)
            
            # Сохранение конфигурации
            await self.save_challenge_config(challenge_config, container)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка развертывания задания: {e}")
            return False
    
    async def build_image(self, challenge_config: Dict[str, Any]):
        """Сборка Docker образа для задания"""
        build_context = self.challenges_dir / challenge_config['build_context']
        
        if not build_context.exists():
            raise ValueError(f"Build context not found: {build_context}")
        
        image_name = f"ctf-challenge-{challenge_config['id']}"
        
        print(f"🏗️ Сборка образа: {image_name}")
        image, logs = self.docker_client.images.build(
            path=str(build_context),
            tag=image_name,
            rm=True
        )
        
        challenge_config['docker_image'] = image_name
    
    async def create_container(self, challenge_config: Dict[str, Any]):
        """Создание контейнера задания"""
        container_config = {
            'image': challenge_config['docker_image'],
            'detach': True,
            'auto_remove': True,
            'network': 'ctf_network',
            'environment': challenge_config.get('environment', {}),
            'ports': challenge_config.get('ports', {})
        }
        
        return self.docker_client.containers.run(**container_config)
    
    async def save_challenge_config(self, challenge_config: Dict[str, Any], container):
        """Сохранение конфигурации задания"""
        config_path = self.challenges_dir / f"{challenge_config['id']}.yaml"
        
        config_data = {
            'challenge': challenge_config,
            'deployment': {
                'container_id': container.id,
                'status': 'running',
                'deployed_at': str(asyncio.get_event_loop().time())
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)