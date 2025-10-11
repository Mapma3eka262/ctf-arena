# backend/check_structure.py
#!/usr/bin/env python3
"""
Скрипт проверки структуры проекта
"""

import os
import sys

def check_directory_structure():
    """Проверка структуры директорий проекта"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        'app',
        'app/api',
        'app/core', 
        'app/models',
        'app/schemas',
        'app/services',
        'app/tasks',
        'app/utils',
        'app/plugins',
        'migrations/versions',
        'frontend/assets/css',
        'frontend/assets/js',
        'frontend/components',
        'frontend/pages',
        'frontend/static',
        'deploy',
        'challenges'
    ]
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/core/__init__.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/core/security.py',
        'app/models/__init__.py',
        'app/api/__init__.py',
        'requirements/base.txt',
        'alembic.ini',
        'Dockerfile',
        'docker-compose.microservices.yml'
    ]
    
    print("🔍 Проверка структуры проекта...")
    
    all_ok = True
    
    # Проверка директорий
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if not os.path.exists(full_path):
            print(f"❌ Отсутствует директория: {dir_path}")
            all_ok = False
        elif not os.path.isdir(full_path):
            print(f"❌ Не является директорией: {dir_path}")
            all_ok = False
    
    # Проверка файлов
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            print(f"❌ Отсутствует файл: {file_path}")
            all_ok = False
        elif not os.path.isfile(full_path):
            print(f"❌ Не является файлом: {file_path}")
            all_ok = False
    
    # Проверка Python модулей
    python_modules = [
        'app.api.auth',
        'app.api.users', 
        'app.api.teams',
        'app.api.challenges',
        'app.api.submissions',
        'app.models.user',
        'app.models.team',
        'app.models.challenge',
        'app.models.submission'
    ]
    
    for module in python_modules:
        try:
            __import__(module)
        except ImportError as e:
            print(f"❌ Ошибка импорта модуля {module}: {e}")
            all_ok = False
    
    if all_ok:
        print("✅ Структура проекта в порядке!")
        return True
    else:
        print("❌ Обнаружены проблемы в структуре проекта")
        return False

def check_dependencies():
    """Проверка установленных зависимостей"""
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import redis
        import docker
        import celery
        import bcrypt
        import jwt
        import requests
        
        print("✅ Основные зависимости установлены")
        return True
        
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        return False

def check_environment():
    """Проверка переменных окружения"""
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY']
    
    print("🔍 Проверка переменных окружения...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    all_ok = True
    
    for var in required_env_vars:
        if not os.getenv(var):
            print(f"❌ Отсутствует переменная окружения: {var}")
            all_ok = False
    
    if all_ok:
        print("✅ Переменные окружения в порядке!")
    else:
        print("⚠️  Установите необходимые переменные окружения")
    
    return all_ok

def main():
    """Основная функция проверки"""
    print("🚀 Проверка проекта CyberCTF Arena...")
    
    checks = [
        check_directory_structure(),
        check_dependencies(), 
        check_environment()
    ]
    
    if all(checks):
        print("\n🎉 Все проверки пройдены! Проект готов к работе.")
        return 0
    else:
        print("\n❌ Обнаружены проблемы. Исправьте их перед запуском.")
        return 1

if __name__ == "__main__":
    sys.exit(main())