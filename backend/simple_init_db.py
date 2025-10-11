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
        """
    ]

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS dynamic_challenges (
        id SERIAL PRIMARY KEY,
        challenge_id INTEGER UNIQUE REFERENCES challenges(id),
        docker_image VARCHAR(255) NOT NULL,
        instance_config JSON NOT NULL,
        resource_limits JSON NOT NULL,
        reset_interval INTEGER DEFAULT 3600,
        max_instances INTEGER DEFAULT 10,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""))

conn.execute(text("""
    CREATE TABLE IF NOT EXISTS challenge_instances (
        id SERIAL PRIMARY KEY,
        dynamic_challenge_id INTEGER NOT NULL REFERENCES dynamic_challenges(id),
        team_id INTEGER NOT NULL REFERENCES teams(id),
        container_id VARCHAR(64) NOT NULL,
        host_port INTEGER NOT NULL,
        internal_port INTEGER NOT NULL,
        flag VARCHAR(500) NOT NULL,
        status VARCHAR(20) DEFAULT 'running',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        last_health_check TIMESTAMP
    )
"""))
    
    for sql in tables_sql:
        cursor.execute(sql)
    
    conn.commit()
    conn.close()
    print(f"✅ SQLite база данных создана: {db_path}")

if __name__ == "__main__":
    init_sqlite()
