#!/bin/bash

# CyberCTF Arena - Integration Script
set -e

echo "🔗 Интеграция фронтенда и бэкенда..."

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

# Создание виртуального окружения Python
echo "🐍 Настройка Python окружения..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей Python
echo "📦 Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."
export PYTHONPATH="$BACKEND_DIR"
python3 -c "
from app.core.database import init_db
from app.core.config import settings
init_db()
print('✅ База данных инициализирована')
"

# Создание системного пользователя для приложения
echo "🔧 Настройка системного пользователя..."
if ! id "ctfapp" &>/dev/null; then
    useradd -r -s /bin/false ctfapp
fi

usermod -a -G ctfapp ctf
chown -R ctfapp:ctfapp $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# Настройка статических файлов
echo "📁 Настройка статических файлов..."
mkdir -p $BACKEND_DIR/static
chown -R ctfapp:ctfapp $BACKEND_DIR/static

# Копирование frontend файлов
echo "🌐 Настройка фронтенда..."
cp -r ./frontend/* $FRONTEND_DIR/
chown -R ctfapp:ctfapp $FRONTEND_DIR

# Создание сервисных файлов systemd
echo "⚙️ Создание systemd сервисов..."

# Backend API сервис
cat > /etc/systemd/system/ctf-api.service << EOF
[Unit]
Description=CyberCTF Arena API
After=network.target postgresql.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Celery worker сервис
cat > /etc/systemd/system/ctf-celery.service << EOF
[Unit]
Description=CyberCTF Arena Celery Worker
After=network.target redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Celery beat сервис
cat > /etc/systemd/system/ctf-celery-beat.service << EOF
[Unit]
Description=CyberCTF Arena Celery Beat
After=network.target redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery beat --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Настройка прав сервисных файлов
chmod 644 /etc/systemd/system/ctf-*.service

echo "✅ Интеграция завершена!"