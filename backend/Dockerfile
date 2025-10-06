FROM python:3.11-slim

# Установка системных зависимостей для Ubuntu
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности
RUN groupadd -r ctf && useradd -r -g ctf ctf
RUN chown -R ctf:ctf /app
USER ctf

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]