#!/bin/bash
# deploy/setup_env.sh

set -e

echo "⚙️ Настройка окружения CyberCTF Arena..."

PROJECT_DIR="/opt/ctf-arena"
ENV_FILE="$PROJECT_DIR/.env"

# Генерация секретного ключа
SECRET_KEY=$(openssl rand -hex 32)

# Получение IP адреса сервера
SERVER_IP=$(curl -s ifconfig.me)

# Создание файла .env
cat > "$ENV_FILE" << EOF
# CyberCTF Arena Environment Configuration
# Generated automatically - edit with care!

# Application Settings
APP_NAME=CyberCTF Arena
APP_VERSION=2.0.0
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://ctfuser:ctfpassword@localhost:5432/ctfarena
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://$SERVER_IP"]

# Email (configure if needed)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# Telegram (configure if needed)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Redis
REDIS_URL=redis://localhost:6379/0

# File Uploads
UPLOAD_DIR=/opt/ctf-arena/uploads
MAX_FILE_SIZE=10485760

# Competition Settings
COMPETITION_START_TIME=2024-09-25T00:00:00
COMPETITION_END_TIME=2024-09-27T23:59:59
MAX_TEAM_SIZE=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ctf-arena/ctf-arena.log

# WebSocket
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001

# Security Settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
ENABLE_AUDIT_LOG=True

# Dynamic Challenges
DOCKER_NETWORK=ctf_network
MAX_CONCURRENT_INSTANCES=50
INSTANCE_TIMEOUT=3600

# Plugins
PLUGINS_ENABLED=True
PLUGINS_DIR=app/plugins

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090
EOF

# Защита файла .env
chmod 600 "$ENV_FILE"
chown ctfapp:ctfapp "$ENV_FILE"

echo "✅ Файл .env создан: $ENV_FILE"
echo "🔐 Секретный ключ сгенерирован"
echo ""
echo "⚠️  Отредактируйте файл .env перед запуском:"
echo "    nano $ENV_FILE"
echo ""
echo "📝 Обязательные настройки:"
echo "   - SMTP настройки для email"
echo "   - Telegram настройки для уведомлений"
echo "   - Время соревнования"
echo "   - Домены в CORS_ORIGINS"