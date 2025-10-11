# backend/app/services/dynamic_service.py
import docker
import asyncio
import secrets
import string
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class DynamicChallengeService:
    """Сервис для управления динамическими заданиями"""
    
    def __init__(self, db: Session):
        self.db = db
        self.docker_client = docker.from_env()
        self.active_containers = {}
    
    async def create_instance(self, challenge_id: int, team_id: int) -> Optional[Dict[str, Any]]:
        """Создание изолированного инстанса задания"""
        # Получаем конфигурацию динамического задания
        from app.models.dynamic_challenge import DynamicChallenge
        dynamic_challenge = self.db.query(DynamicChallenge).filter(
            DynamicChallenge.id == challenge_id
        ).first()
        
        if not dynamic_challenge:
            return None
        
        # Генерируем уникальный флаг
        flag = self._generate_flag()
        
        # Конфигурация контейнера
        container_config = {
            'image': dynamic_challenge.docker_image,
            'environment': {
                'TEAM_ID': str(team_id),
                'CHALLENGE_ID': str(challenge_id),
                'FLAG': flag,
                **dynamic_challenge.instance_config.get('environment', {})
            },
            'ports': self._get_port_mapping(dynamic_challenge),
            'network': 'ctf_network',
            'detach': True,
            'auto_remove': True,
            'mem_limit': dynamic_challenge.resource_limits.get('memory', '100m'),
            'cpu_shares': dynamic_challenge.resource_limits.get('cpu', 1024)
        }
        
        try:
            # Запускаем контейнер
            container = self.docker_client.containers.run(**container_config)
            
            # Сохраняем инстанс в базе
            from app.models.dynamic_challenge import ChallengeInstance
            instance = ChallengeInstance(
                dynamic_challenge_id=challenge_id,
                team_id=team_id,
                container_id=container.id,
                host_port=self._extract_host_port(container, dynamic_challenge),
                internal_port=dynamic_challenge.instance_config['internal_port'],
                flag=flag,
                expires_at=datetime.utcnow() + timedelta(seconds=dynamic_challenge.reset_interval)
            )
            
            self.db.add(instance)
            self.db.commit()
            
            return {
                "instance_id": instance.id,
                "host": "localhost",  # В production заменить на реальный хост
                "port": instance.host_port,
                "status": "running",
                "expires_at": instance.expires_at.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Ошибка создания инстанса: {e}")
            return None
    
    async def destroy_instance(self, instance_id: int) -> bool:
        """Уничтожение инстанса задания"""
        from app.models.dynamic_challenge import ChallengeInstance
        
        instance = self.db.query(ChallengeInstance).filter(
            ChallengeInstance.id == instance_id
        ).first()
        
        if not instance:
            return False
        
        try:
            container = self.docker_client.containers.get(instance.container_id)
            container.stop()
            
            instance.status = "stopped"
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка остановки инстанса: {e}")
            return False
    
    async def health_check_instances(self):
        """Проверка здоровья всех активных инстансов"""
        from app.models.dynamic_challenge import ChallengeInstance
        
        instances = self.db.query(ChallengeInstance).filter(
            ChallengeInstance.status == "running"
        ).all()
        
        for instance in instances:
            try:
                container = self.docker_client.containers.get(instance.container_id)
                if container.status != "running":
                    instance.status = "stopped"
                else:
                    instance.last_health_check = datetime.utcnow()
            except:
                instance.status = "error"
        
        self.db.commit()
    
    async def cleanup_expired_instances(self):
        """Очистка просроченных инстансов"""
        from app.models.dynamic_challenge import ChallengeInstance
        
        expired_instances = self.db.query(ChallengeInstance).filter(
            ChallengeInstance.expires_at < datetime.utcnow(),
            ChallengeInstance.status == "running"
        ).all()
        
        for instance in expired_instances:
            await self.destroy_instance(instance.id)
    
    def _generate_flag(self) -> str:
        """Генерация уникального флага"""
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        return f"CTF{{{random_part}}}"
    
    def _get_port_mapping(self, dynamic_challenge: DynamicChallenge) -> Dict[str, int]:
        """Создание маппинга портов для Docker"""
        internal_port = dynamic_challenge.instance_config['internal_port']
        return {f"{internal_port}/tcp": None}  # Docker выберет случайный порт
    
    def _extract_host_port(self, container, dynamic_challenge: DynamicChallenge) -> int:
        """Извлечение хостового порта из контейнера"""
        internal_port = dynamic_challenge.instance_config['internal_port']
        port_info = container.ports.get(f"{internal_port}/tcp")
        if port_info:
            return int(port_info[0]['HostPort'])
        return 0