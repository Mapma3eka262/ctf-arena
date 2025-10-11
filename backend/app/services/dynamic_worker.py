# backend/app/services/dynamic_worker.py
import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.dynamic_service import DynamicChallengeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicChallengeWorker:
    """Воркер для управления динамическими заданиями"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.dynamic_service = DynamicChallengeService(self.db)
        self.running = True
    
    async def start(self):
        """Запуск воркера"""
        logger.info("🚀 Запуск Dynamic Challenge Worker")
        
        try:
            while self.running:
                await self.process_tasks()
                await asyncio.sleep(60)  # Проверка каждую минуту
        except Exception as e:
            logger.error(f"❌ Ошибка воркера: {e}")
        finally:
            self.db.close()
    
    async def process_tasks(self):
        """Обработка задач воркера"""
        try:
            # Проверка здоровья инстансов
            await self.dynamic_service.health_check_instances()
            logger.info("✅ Проверка здоровья инстансов завершена")
            
            # Очистка просроченных инстансов
            await self.dynamic_service.cleanup_expired_instances()
            logger.info("✅ Очистка просроченных инстансов завершена")
            
            # Статистика
            await self.log_statistics()
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки задач: {e}")
    
    async def log_statistics(self):
        """Логирование статистики"""
        from app.models.dynamic_challenge import ChallengeInstance
        
        total_instances = self.db.query(ChallengeInstance).count()
        running_instances = self.db.query(ChallengeInstance).filter(
            ChallengeInstance.status == "running"
        ).count()
        
        logger.info(f"📊 Статистика инстансов: {running_instances}/{total_instances} запущено")
    
    def stop(self):
        """Остановка воркера"""
        self.running = False
        logger.info("🛑 Остановка Dynamic Challenge Worker")

async def main():
    worker = DynamicChallengeWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()

if __name__ == "__main__":
    asyncio.run(main())