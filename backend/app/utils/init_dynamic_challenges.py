# backend/app/utils/init_dynamic_challenges.py
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.challenge import Challenge
from app.models.dynamic_challenge import DynamicChallenge

async def init_dynamic_challenges():
    """Инициализация демо-динамических заданий"""
    db = SessionLocal()
    
    try:
        # Пример динамического задания - Web уязвимость
        web_challenge = Challenge(
            title="Web Security Challenge",
            description="Найдите уязвимость в веб-приложении",
            category="WEB",
            difficulty="medium",
            points=200,
            flag="CTF{dynamic_web_flag}",
            is_active=True
        )
        
        db.add(web_challenge)
        db.flush()  # Получаем ID
        
        dynamic_web = DynamicChallenge(
            id=web_challenge.id,
            docker_image="ctf-web-challenge:latest",
            instance_config={
                "internal_port": 80,
                "environment": {
                    "SECRET_KEY": "dynamic_secret_key"
                }
            },
            reset_interval=3600,
            max_instances=10,
            resource_limits={
                "memory": "128m",
                "cpu": 512
            }
        )
        
        db.add(dynamic_web)
        db.commit()
        
        print("✅ Демо-динамические задания созданы")
        
    except Exception as e:
        print(f"❌ Ошибка создания демо-заданий: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(init_dynamic_challenges())