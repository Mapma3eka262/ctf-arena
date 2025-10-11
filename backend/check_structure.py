#!/usr/bin/env python3
"""
Скрипт проверки структуры проекта
"""

import os
import sys

def get_project_root():
    """Получить корневую директорию проекта"""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(current_file))

def check_directory_structure():
    """Проверка структуры директорий проекта"""
    base_dir = get_project_root()
    
    required_dirs = [
        'backend/app',
        'backend/app/api',
        'backend/app/core', 
        'backend/app/models',
        'backend/app/schemas',
        'backend/app/services',
        'backend/app/tasks',
        'backend/app/utils',
        'backend/app/plugins',
        'backend/migrations/versions',
        'frontend/assets/css',
        'frontend/assets/js',
        'frontend/components',
        'frontend/pages',
        'frontend/static',
        'deploy',
        'challenges'
    ]
    
    required_files = [
        'backend/app/__init__.py',
        'backend/app/main.py',
        'backend/app/core/__init__.py',
        'backend/app/core/config.py',
        'backend/app/core/database.py',
        'backend/app/core/security.py',
        'backend/app/models/__init__.py',
        'backend/app/api/__init__.py',
        'backend/requirements/base.txt',
        'backend/alembic.ini',
        'backend/Dockerfile',
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
    
    # Проверка Python модулей (через файлы)
    python_module_files = [
        'backend/app/api/auth.py',
        'backend/app/api/users.py', 
        'backend/app/api/teams.py',
        'backend/app/api/challenges.py',
        'backend/app/api/submissions.py',
        'backend/app/models/user.py',
        'backend/app/models/team.py',
        'backend/app/models/challenge.py',
        'backend/app/models/submission.py'
    ]
    
    for module_file in python_module_files:
        full_path = os.path.join(base_dir, module_file)
        if not os.path.exists(full_path):
            print(f"❌ Отсутствует файл модуля: {module_file}")
            all_ok = False
    
    if all_ok:
        print("✅ Структура проекта в порядке!")
        return True
    else:
        print("❌ Обнаружены проблемы в структуре проекта")
        return False

def check_dependencies():
    """Проверка установленных зависимостей"""
    dependencies = {
        'fastapi': 'fastapi',
        'sqlalchemy': 'sqlalchemy',
        'pydantic': 'pydantic',
        'redis': 'redis',
        'docker': 'docker',
        'celery': 'celery',
        'bcrypt': 'bcrypt',
        'jwt': 'PyJWT',
        'requests': 'requests'
    }
    
    print("🔍 Проверка зависимостей...")
    
    all_ok = True
    
    for package, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ Отсутствует: {package}")
            all_ok = False
    
    return all_ok

def check_environment():
    """Проверка переменных окружения"""
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY']
    
    print("🔍 Проверка переменных окружения...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv загружен")
    except ImportError:
        print("⚠️  dotenv не установлен")
    
    all_ok = True
    
    for var in required_env_vars:
        if not os.getenv(var):
            print(f"❌ Отсутствует переменная окружения: {var}")
            all_ok = False
        else:
            print(f"✅ {var}")
    
    if all_ok:
        print("✅ Переменные окружения в порядке!")
    else:
        print("⚠️  Установите необходимые переменные окружения")
    
    return all_ok

def main():
    """Основная функция проверки"""
    print("🚀 Проверка проекта CyberCTF Arena...")
    print(f"📁 Корневая директория: {get_project_root()}")
    
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
