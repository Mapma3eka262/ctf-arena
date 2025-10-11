#!/usr/bin/env python3
"""
Упрощенная инициализация БД с использованием чистого SQL
"""

import sqlite3
import os
import sys

def init_sqlite():
    """Инициализация SQLite базы данных"""
    db_path = 'ctf_arena.db'
    
    if os.path.exists(db_path):
        print(f"⚠️ База данных {db_path} уже существует")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицы
    tables_sql = [
        # teams table
        """
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # users table  
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            team_id INTEGER REFERENCES teams(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # challenges table
        """
        CREATE TABLE challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            points INTEGER NOT NULL,
            flag TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # dynamic_challenges table
        """
        CREATE TABLE dynamic_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER UNIQUE REFERENCES challenges(id),
            docker_image TEXT NOT NULL,
            instance_config TEXT NOT NULL,
            resource_limits TEXT NOT NULL,
            reset_interval INTEGER DEFAULT 3600,
            max_instances INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # challenge_instances table
        """
        CREATE TABLE challenge_instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dynamic_challenge_id INTEGER NOT NULL REFERENCES dynamic_challenges(id),
            team_id INTEGER NOT NULL REFERENCES teams(id),
            container_id TEXT NOT NULL,
            host_port INTEGER NOT NULL,
            internal_port INTEGER NOT NULL,
            flag TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            last_health_check TIMESTAMP
        )
        """,
        # notifications table
        """
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            category TEXT DEFAULT 'system',
            is_read BOOLEAN DEFAULT FALSE,
            action_url TEXT,
            notification_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        )
        """,
        # invitations table
        """
        CREATE TABLE invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending',
            expires_at TIMESTAMP NOT NULL,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            invited_by_id INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # submissions table
        """
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_flag TEXT NOT NULL,
            status TEXT NOT NULL,
            points_awarded INTEGER DEFAULT 0,
            is_first_blood BOOLEAN DEFAULT FALSE,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            challenge_id INTEGER NOT NULL REFERENCES challenges(id),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # services table
        """
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            check_endpoint TEXT,
            expected_status INTEGER DEFAULT 200,
            is_active BOOLEAN DEFAULT TRUE,
            status TEXT DEFAULT 'unknown',
            last_checked TIMESTAMP,
            response_time INTEGER,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # competitions table
        """
        CREATE TABLE competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            rules TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            is_public BOOLEAN DEFAULT TRUE,
            max_team_size INTEGER DEFAULT 5,
            scoring_type TEXT DEFAULT 'dynamic',
            allowed_categories TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    print("📝 Создание таблиц базы данных...")
    
    for i, sql in enumerate(tables_sql, 1):
        try:
            cursor.execute(sql)
            table_name = sql.split("CREATE TABLE")[1].split("(")[0].strip()
            print(f"✅ Таблица {table_name} создана ({i}/{len(tables_sql)})")
        except Exception as e:
            print(f"❌ Ошибка создания таблицы: {e}")
    
    # Создаем тестовые данные
    create_test_data(cursor)
    
    conn.commit()
    conn.close()
    print(f"🎉 SQLite база данных создана: {db_path}")

def create_test_data(cursor):
    """Создание тестовых данных"""
    try:
        print("📊 Создание тестовых данных...")
        
        # Создаем тестовую команду
        cursor.execute("""
            INSERT INTO teams (name, description, score) 
            VALUES ('Test Team', 'Тестовая команда для разработки', 0)
        """)
        team_id = cursor.lastrowid
        
        # Создаем тестового пользователя (пароль: admin123)
        import hashlib
        hashed_password = hashlib.sha256(b"admin123").hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, is_admin, team_id)
            VALUES ('admin', 'admin@ctf-arena.local', ?, TRUE, ?)
        """, (hashed_password, team_id))
        
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, is_admin, team_id)
            VALUES ('user1', 'user1@ctf-arena.local', ?, FALSE, ?)
        """, (hashed_password, team_id))
        
        # Создаем тестовые задания
        challenges_data = [
            ('Welcome Challenge', 'Простое задание для знакомства с платформой', 'MISC', 'easy', 50, 'CTF{w3lc0m3_t0_ctf_4r3n4}'),
            ('Web Security 101', 'Базовое задание по веб-безопасности', 'WEB', 'easy', 100, 'CTF{w3b_s3cur1ty_b4s1c5}'),
            ('Crypto Challenge', 'Задание по криптографии для начинающих', 'CRYPTO', 'easy', 100, 'CTF{cryp70_b4s1c5}'),
            ('Reverse Engineering', 'Простое задание по реверс-инжинирингу', 'REVERSE', 'medium', 200, 'CTF{r3v3rs3_3ng1n33r1ng}')
        ]
        
        for challenge in challenges_data:
            cursor.execute("""
                INSERT INTO challenges (title, description, category, difficulty, points, flag)
                VALUES (?, ?, ?, ?, ?, ?)
            """, challenge)
        
        # Создаем тестовые сервисы для мониторинга
        services_data = [
            ('CTF API', 'web', 'localhost', 8000, '/api/health', 200),
            ('PostgreSQL', 'database', 'localhost', 5432, None, None),
            ('Redis', 'cache', 'localhost', 6379, None, None),
            ('Frontend', 'web', 'localhost', 3000, '/', 200)
        ]
        
        for service in services_data:
            cursor.execute("""
                INSERT INTO services (name, type, host, port, check_endpoint, expected_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, service)
        
        print("✅ Тестовые данные созданы")
        print("👤 Учетные записи для тестирования:")
        print("   Администратор: admin / admin123")
        print("   Пользователь:  user1 / admin123")
        
    except Exception as e:
        print(f"⚠️ Ошибка при создании тестовых данных: {e}")

if __name__ == "__main__":
    init_sqlite()
