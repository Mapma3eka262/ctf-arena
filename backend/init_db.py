# backend/init_db.py
#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для CyberCTF Arena
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, check_db_connection
from app.core.config import settings

def main():
    """Основная функция инициализации"""
    print("🚀 Инициализация базы данных CyberCTF Arena...")
    
    # Проверка подключения к базе данных
    print("🔍 Проверка подключения к базе данных...")
    if not check_db_connection():
        print("❌ Не удалось подключиться к базе данных")
        print(f"   URL: {settings.DATABASE_URL}")
        sys.exit(1)
    
    print("✅ Подключение к базе данных успешно")
    
    # Создание таблиц
    print("🗄️ Создание таблиц...")
    try:
        init_db()
        print("✅ Таблицы созданы успешно")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        sys.exit(1)
    
    # Создание тестовых данных
    print("📝 Создание тестовых данных...")
    try:
        create_test_data()
        print("✅ Тестовые данные созданы")
    except Exception as e:
        print(f"⚠️ Ошибка при создании тестовых данных: {e}")
    
    print("\n🎉 Инициализация базы данных завершена!")
    print("\n👤 Тестовые учетные записи:")
    print("   Администратор: admin / admin123")
    print("   (Пароль можно изменить после входа)")

def create_test_data():
    """Создание тестовых данных"""
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.team import Team
    from app.models.challenge import Challenge
    from app.models.service import Service
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    try:
        # Создание тестовой команды
        team = Team(name="Test Team", score=0)
        db.add(team)
        db.flush()  # Получаем ID команды
        
        # Создание администратора
        admin_user = User(
            username="admin",
            email="admin@ctf-arena.local",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_captain=True,
            team_id=team.id,
            is_active=True
        )
        db.add(admin_user)
        
        # Создание тестовых заданий
        challenges = [
            Challenge(
                title="Welcome Challenge",
                description="Простое задание для знакомства с платформой. Найдите флаг в описании.",
                category="MISC",
                difficulty="easy",
                points=50,
                flag="CTF{w3lc0m3_t0_ctf_4r3n4}",
                hint="Флаг прямо перед вами!",
                is_active=True,
                is_visible=True
            ),
            Challenge(
                title="Web Security 101",
                description="Базовое задание по веб-безопасности. Проверьте свои знания.",
                category="WEB",
                difficulty="easy",
                points=100,
                flag="CTF{w3b_s3cur1ty_b4s1c5}",
                hint="Попробуйте проанализировать исходный код",
                is_active=True,
                is_visible=True
            ),
            Challenge(
                title="Crypto Challenge",
                description="Задание по криптографии для начинающих.",
                category="CRYPTO",
                difficulty="easy",
                points=100,
                flag="CTF{cryp70_b4s1c5}",
                hint="Используйте базовые методы шифрования",
                is_active=True,
                is_visible=True
            ),
            Challenge(
                title="Forensics Investigation",
                description="Расследование цифровых улик. Найдите скрытую информацию.",
                category="FORENSICS",
                difficulty="medium",
                points=200,
                flag="CTF{f0r3ns1c5_m4st3r}",
                hint="Проверьте метаданные файлов",
                is_active=True,
                is_visible=True
            ),
            Challenge(
                title="Reverse Engineering",
                description="Обратная разработка приложения. Анализ бинарного кода.",
                category="REVERSING",
                difficulty="hard",
                points=300,
                flag="CTF{r3v3rs3_3ng1n33r1ng}",
                hint="Используйте инструменты для дизассемблирования",
                is_active=True,
                is_visible=True
            )
        ]
        
        for challenge in challenges:
            db.add(challenge)
        
        # Создание сервисов для мониторинга
        services = [
            Service(
                name="CTF API",
                type="web",
                host="localhost",
                port=8000,
                check_endpoint="/api/health",
                expected_status=200,
                is_active=True
            ),
            Service(
                name="PostgreSQL",
                type="database",
                host="localhost",
                port=5432,
                is_active=True
            ),
            Service(
                name="Redis",
                type="database", 
                host="localhost",
                port=6379,
                is_active=True
            ),
            Service(
                name="WebSocket Server",
                type="web",
                host="localhost", 
                port=8001,
                check_endpoint="/health",
                expected_status=200,
                is_active=True
            )
        ]
        
        for service in services:
            db.add(service)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()