# backend/simple_init_db.py
#!/usr/bin/env python3
"""
Простой скрипт инициализации базы данных без зависимостей от проблемных библиотек
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Основная функция инициализации БД"""
    print("🚀 Простая инициализация базы данных CyberCTF Arena...")
    
    try:
        # Импортируем только необходимые компоненты
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        # Создаем движок базы данных
        engine = create_engine(settings.DATABASE_URL)
        
        # Создаем таблицы с помощью прямых SQL запросов
        with engine.connect() as conn:
            # Включаем транзакцию
            trans = conn.begin()
            
            try:
                # Создаем таблицу команд
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS teams (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        description TEXT,
                        score INTEGER DEFAULT 0,
                        avatar_url VARCHAR(255),
                        country VARCHAR(50),
                        website VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу пользователей
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        first_name VARCHAR(50),
                        last_name VARCHAR(50),
                        is_active BOOLEAN DEFAULT TRUE,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_captain BOOLEAN DEFAULT FALSE,
                        team_id INTEGER REFERENCES teams(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу заданий
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS challenges (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        difficulty VARCHAR(20) NOT NULL,
                        points INTEGER NOT NULL,
                        flag VARCHAR(500) NOT NULL,
                        hint TEXT,
                        files TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_visible BOOLEAN DEFAULT TRUE,
                        solved_count INTEGER DEFAULT 0,
                        first_blood_user_id INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу отправок
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS submissions (
                        id SERIAL PRIMARY KEY,
                        flag VARCHAR(500) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        points_awarded INTEGER DEFAULT 0,
                        is_first_blood BOOLEAN DEFAULT FALSE,
                        team_id INTEGER NOT NULL REFERENCES teams(id),
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        challenge_id INTEGER NOT NULL REFERENCES challenges(id),
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу сервисов
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS services (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        host VARCHAR(100) NOT NULL,
                        port INTEGER NOT NULL,
                        check_endpoint VARCHAR(100),
                        expected_status INTEGER DEFAULT 200,
                        is_active BOOLEAN DEFAULT TRUE,
                        status VARCHAR(20) DEFAULT 'unknown',
                        last_checked TIMESTAMP,
                        response_time INTEGER,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу приглашений
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS invitations (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(100) NOT NULL,
                        token VARCHAR(100) UNIQUE NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        expires_at TIMESTAMP NOT NULL,
                        team_id INTEGER NOT NULL REFERENCES teams(id),
                        invited_by_id INTEGER NOT NULL REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Создаем таблицу соревнований
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS competitions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        rules TEXT,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT FALSE,
                        is_public BOOLEAN DEFAULT TRUE,
                        max_team_size INTEGER DEFAULT 5,
                        scoring_type VARCHAR(20) DEFAULT 'dynamic',
                        allowed_categories TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Фиксируем транзакцию
                trans.commit()
                print("✅ Таблицы базы данных успешно созданы")
                
                # Создаем тестовые данные
                create_test_data(conn)
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Ошибка при создании таблиц: {e}")
                raise
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        sys.exit(1)

def create_test_data(conn):
    """Создание тестовых данных"""
    from sqlalchemy import text
    import bcrypt
    
    try:
        # Создаем тестовую команду
        result = conn.execute(text("""
            INSERT INTO teams (name, score) 
            VALUES ('Test Team', 0)
            RETURNING id
        """))
        team_id = result.fetchone()[0]
        
        # backend/simple_init_db.py (продолжение)

        # Создаем тестового пользователя (пароль: admin123)
        hashed_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
        
        conn.execute(text("""
            INSERT INTO users (username, email, hashed_password, is_admin, is_captain, team_id)
            VALUES ('admin', 'admin@ctf-arena.local', :password, TRUE, TRUE, :team_id)
        """), {"password": hashed_password, "team_id": team_id})
        
        # Создаем тестовые задания
        challenges_data = [
            {
                'title': 'Welcome Challenge',
                'description': 'Простое задание для знакомства с платформой',
                'category': 'MISC',
                'difficulty': 'easy',
                'points': 50,
                'flag': 'CTF{w3lc0m3_t0_ctf_4r3n4}'
            },
            {
                'title': 'Web Security 101', 
                'description': 'Базовое задание по веб-безопасности',
                'category': 'WEB',
                'difficulty': 'easy',
                'points': 100,
                'flag': 'CTF{w3b_s3cur1ty_b4s1c5}'
            },
            {
                'title': 'Crypto Challenge',
                'description': 'Задание по криптографии для начинающих',
                'category': 'CRYPTO', 
                'difficulty': 'easy',
                'points': 100,
                'flag': 'CTF{cryp70_b4s1c5}'
            }
        ]
        
        for challenge in challenges_data:
            conn.execute(text("""
                INSERT INTO challenges (title, description, category, difficulty, points, flag)
                VALUES (:title, :description, :category, :difficulty, :points, :flag)
            """), challenge)
        
        # Создаем тестовые сервисы для мониторинга
        services_data = [
            ('CTF API', 'web', 'localhost', 8000, '/api/health', 200),
            ('PostgreSQL', 'database', 'localhost', 5432, None, None),
            ('Redis', 'database', 'localhost', 6379, None, None)
        ]
        
        for service in services_data:
            conn.execute(text("""
                INSERT INTO services (name, type, host, port, check_endpoint, expected_status)
                VALUES (:name, :type, :host, :port, :endpoint, :status)
            """), {
                "name": service[0],
                "type": service[1], 
                "host": service[2],
                "port": service[3],
                "endpoint": service[4],
                "status": service[5]
            })
        
        print("✅ Тестовые данные успешно созданы")
        print("👤 Администратор: admin / admin123")
        
    except Exception as e:
        print(f"⚠️ Ошибка при создании тестовых данных: {e}")

if __name__ == "__main__":
    main()