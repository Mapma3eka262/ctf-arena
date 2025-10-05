import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

def generate_random_string(length: int = 32) -> str:
    """Генерация случайной строки"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_verification_token() -> str:
    """Генерация токена для верификации"""
    return generate_random_string(32)

def format_duration(seconds: int) -> str:
    """Форматирование длительности в читаемый вид"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def calculate_score_decay(base_score: int, solve_time: datetime, start_time: datetime, end_time: datetime) -> int:
    """Расчет decay счета в зависимости от времени решения"""
    total_duration = (end_time - start_time).total_seconds()
    solve_duration = (solve_time - start_time).total_seconds()
    
    # Linear decay from 100% to 50%
    decay_factor = 0.5 + (0.5 * (1 - solve_duration / total_duration))
    
    return int(base_score * decay_factor)

def sanitize_input(text: str) -> str:
    """Очистка пользовательского ввода от потенциально опасных символов"""
    if not text:
        return text
    
    # Удаляем или экранируем потенциально опасные символы
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def get_time_until(target_time: datetime) -> Optional[timedelta]:
    """Получение времени до указанной даты"""
    if not target_time:
        return None
    
    now = datetime.utcnow()
    if now >= target_time:
        return timedelta(0)
    
    return target_time - now