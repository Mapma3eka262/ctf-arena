import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Валидация имени пользователя"""
    if len(username) < 3 or len(username) > 50:
        return False
    
    # Разрешаем буквы, цифры, подчеркивания и дефисы
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, username) is not None

def validate_team_name(name: str) -> bool:
    """Валидация названия команды"""
    if len(name) < 2 or len(name) > 100:
        return False
    
    # Разрешаем буквы, цифры, пробелы и основные символы
    pattern = r'^[a-zA-Z0-9\s\-_\.]+$'
    return re.match(pattern, name) is not None

def validate_flag_format(flag: str) -> bool:
    """Валидация формата флага"""
    return flag.startswith("CTF{") and flag.endswith("}") and len(flag) > 6

def validate_ip_address(ip: str) -> bool:
    """Валидация IP-адреса"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    for part in parts:
        if not 0 <= int(part) <= 255:
            return False
    
    return True

def validate_url(url: str) -> bool:
    """Валидация URL"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None