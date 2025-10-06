import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List
import json

def generate_random_string(length: int = 10) -> str:
    """Генерация случайной строки"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def format_time_remaining(seconds: int) -> str:
    """Форматирование оставшегося времени"""
    if seconds <= 0:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_success_rate(total: int, successful: int) -> float:
    """Расчет процента успеха"""
    if total == 0:
        return 0.0
    return round((successful / total) * 100, 2)

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Безопасная загрузка JSON"""
    if not json_string:
        return default
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any) -> str:
    """Безопасная сериализация в JSON"""
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return "{}"

def filter_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Фильтрация чувствительных данных для логов"""
    sensitive_fields = ['password', 'token', 'secret', 'key', 'flag']
    filtered_data = data.copy()
    
    for field in sensitive_fields:
        if field in filtered_data:
            filtered_data[field] = '***HIDDEN***'
    
    return filtered_data

def get_current_competition_time() -> Dict[str, datetime]:
    """Получение времени текущего соревнования"""
    # В реальной системе здесь будет запрос к базе данных
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=48)  # Пример: 48 часов
    
    return {
        "start_time": start_time,
        "end_time": end_time,
        "current_time": datetime.utcnow()
    }

def paginate_data(data: List[Any], page: int, page_size: int) -> Dict[str, Any]:
    """Пагинация данных"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_data = data[start_idx:end_idx]
    
    return {
        "data": paginated_data,
        "page": page,
        "page_size": page_size,
        "total": len(data),
        "total_pages": (len(data) + page_size - 1) // page_size,
        "has_next": end_idx < len(data),
        "has_prev": page > 1
    }

def format_file_size(size_bytes: int) -> str:
    """Форматирование размера файла"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от опасных символов"""
    import re
    # Удаляем опасные символы
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Ограничиваем длину
    filename = filename[:100]
    return filename