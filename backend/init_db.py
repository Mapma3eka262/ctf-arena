#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для CyberCTF Arena
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base, init_db
from app.core.config import settings

def main():
    """Основная функция инициализации БД"""
    print("🚀 Инициализация базы данных CyberCTF Arena...")
    
    try:
        # Инициализация базы данных
        init_db()
        print("✅ База данных успешно инициализирована")
        
        # Создание тестовых данных (опционально)
        create_test_data()
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        sys.exit(1)

def create_test_data():
    """Создание тестовых данных"""
    try:
        from sqlalchemy.orm import Session
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.models.team import Team
        from app.models.challenge import Challenge
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        # Создание тестовой команды и пользователя
        team = Team(name="Test Team", score=0)
        db.add(team)
        db.flush()  # Получаем ID команды
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_captain=True,
            team_id=team.id
        )
        db.add(user)
        
        # Создание тестовых заданий
        challenges = [
            Challenge(
                title="Web Security 101",
                description="Базовое задание по веб-безопасности",
                category="WEB",
                difficulty="easy",
                points=100,
                flag="CTF{web_security_basic}"
            ),
            Challenge(
                title="Crypto Challenge",
                description="Задание по криптографии",
                category="Crypto", 
                difficulty="medium",
                points=200,
                flag="CTF{crypto_is_fun}"
            ),
            Challenge(
                title="Forensics Investigation",
                description="Расследование цифровых улик",
                category="Forensics",
                difficulty="hard", 
                points=300,
                flag="CTF{forensics_master}"
            )
        ]
        
        for challenge in challenges:
            db.add(challenge)
        
        db.commit()
        print("✅ Тестовые данные созданы")
        
    except Exception as e:
        print(f"⚠️  Не удалось создать тестовые данные: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
