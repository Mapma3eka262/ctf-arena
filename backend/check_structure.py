#!/usr/bin/env python3
"""
Скрипт проверки структуры проекта
"""

import os
import sys

def check_structure():
    """Проверка наличия всех необходимых файлов"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py", 
        "app/core/config.py",
        "app/core/database.py",
        "app/core/security.py",
        "app/core/auth.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/team.py", 
        "app/models/challenge.py",
        "app/models/submission.py",
        "app/models/invitation.py",
        "app/schemas/__init__.py",
        "app/schemas/auth.py",
        "app/schemas/user.py",
        "app/schemas/team.py",
        "app/schemas/challenge.py", 
        "app/schemas/submission.py",
        "app/schemas/invitation.py",
        "app/api/__init__.py",
        "app/api/auth.py",
        "app/api/users.py",
        "app/api/teams.py",
        "app/api/challenges.py",
        "app/api/submissions.py",
        "requirements.txt"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Отсутствуют следующие файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Все необходимые файлы присутствуют")
        return True

if __name__ == "__main__":
    if check_structure():
        sys.exit(0)
    else:
        sys.exit(1)
