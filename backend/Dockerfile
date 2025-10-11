# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements/prod.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r prod.txt

# Копирование приложения
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 ctfapp && chown -R ctfapp:ctfapp /app
USER ctfapp

# Экспорт портов
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]