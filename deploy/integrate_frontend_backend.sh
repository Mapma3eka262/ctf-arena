#!/bin/bash

# CyberCTF Arena - Fixed Integration Script for Ubuntu 24.04
set -e

echo "🔗 Интеграция фронтенда и бэкенда (исправленная версия)..."

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root"
    exit 1
fi

# Переменные
PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
NGINX_DIR="/etc/nginx"

# Проверка существования директорий
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Директория backend не найдена: $BACKEND_DIR"
    echo "Скопируйте файлы backend в эту директорию"
    exit 1
fi

# Создание виртуального окружения Python
echo "🐍 Настройка Python окружения..."
cd $BACKEND_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "⚠️  Виртуальное окружение уже существует"
fi

source venv/bin/activate

# Установка исправленных зависимостей Python
echo "📦 Установка Python зависимостей (исправленные версии)..."
pip install --upgrade pip

# Устанавливаем bcrypt отдельно с правильными флагами
pip install "bcrypt==4.1.1" --no-build-isolation

if [ -f "requirements.txt" ]; then
    # Устанавливаем остальные зависимости
    pip install -r requirements.txt --no-deps
    # Затем устанавливаем зависимости без версий для разрешения конфликтов
    pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-jose requests python-dotenv celery redis
    echo "✅ Зависимости установлены"
else
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."

# Проверка доступности PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL не запущен"
    systemctl start postgresql
    echo "✅ PostgreSQL запущен"
fi

# Используем простой скрипт для инициализации БД
if [ -f "simple_init_db.py" ]; then
    python3 simple_init_db.py
else
    # Альтернативный метод с обработкой ошибок bcrypt
    echo "⚠️  Используем альтернативный метод инициализации..."
    export PYTHONPATH="$BACKEND_DIR"
    python3 -c "
import sys
import os
sys.path.append('$BACKEND_DIR')

try:
    # Пытаемся использовать простую инициализацию
    from sqlalchemy import create_engine, text
    from app.core.config import settings
    
    print('Создание таблиц базы данных...')
    engine = create_engine(settings.DATABASE_URL)
    
    # Простая проверка подключения
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
        print('✅ Подключение к базе данных успешно')
    
    # Импортируем и запускаем стандартную инициализацию
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ Таблицы базы данных созданы')
    
except Exception as e:
    print(f'❌ Ошибка инициализации БД: {e}')
    print('Попробуйте запустить simple_init_db.py вручную')
    sys.exit(1)
"
fi

# Настройка статических файлов
echo "📁 Настройка статических файлов..."
mkdir -p $BACKEND_DIR/static
chown -R ctfapp:ctfapp $BACKEND_DIR/static

# Копирование frontend файлов (если они существуют)
echo "🌐 Настройка фронтенда..."
if [ -d "./frontend" ]; then
    cp -r ./frontend/* $FRONTEND_DIR/ 2>/dev/null || true
    echo "✅ Файлы фронтенда скопированы"
else
    echo "⚠️  Директория frontend не найдена, пропускаем"
fi

chown -R ctfapp:ctfapp $FRONTEND_DIR 2>/dev/null || true

# Создание сервисных файлов systemd
echo "⚙️ Создание systemd сервисов..."

# Backend API сервис
cat > /etc/systemd/system/ctf-api.service << EOF
[Unit]
Description=CyberCTF Arena API
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Celery worker сервис
cat > /etc/systemd/system/ctf-celery.service << EOF
[Unit]
Description=CyberCTF Arena Celery Worker
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery worker --loglevel=info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Celery beat сервис
cat > /etc/systemd/system/ctf-celery-beat.service << EOF
[Unit]
Description=CyberCTF Arena Celery Beat
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery beat --loglevel=info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Настройка прав сервисных файлов
chmod 644 /etc/systemd/system/ctf-*.service

# Перезагрузка systemd
systemctl daemon-reload

# Включение сервисов
systemctl enable ctf-api ctf-celery ctf-celery-beat

echo "✅ Интеграция завершена!"
echo ""
echo "Сервисы созданы и включены:"
echo "  ctf-api.service"
echo "  ctf-celery.service" 
echo "  ctf-celery-beat.service"
echo ""
echo "Для запуска используйте:"
echo "  sudo systemctl start ctf-api ctf-celery ctf-celery-beat"
echo "  sudo systemctl status ctf-api"
