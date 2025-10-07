#!/bin/bash

# CyberCTF Arena - Environment Setup Script
set -e

echo "⚙️  Настройка окружения CyberCTF Arena..."

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root: sudo ./setup_env.sh"
    exit 1
fi

PROJECT_DIR="/opt/ctf-arena"
ENV_FILE="$PROJECT_DIR/.env"

# Создаем .env файл если он не существует
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Создание файла .env..."
    
    # Генерируем случайный секретный ключ
    SECRET_KEY=$(openssl rand -hex 32)
    
    cat > "$ENV_FILE" << EOF
# CyberCTF Arena Environment Configuration
# Generated automatically - review and modify as needed

# Application Settings
APP_NAME=CyberCTF Arena
APP_VERSION=1.0.0
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://ctfuser:ctfpassword@localhost:5432/ctfarena

# JWT Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Origins
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]

# Email Configuration (optional)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Telegram Bot (optional)
# TELEGRAM_BOT_TOKEN=your-telegram-bot-token
# TELEGRAM_CHAT_ID=your-chat-id

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# File Uploads
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Competition Settings
COMPETITION_START_TIME=2024-09-25T00:00:00
COMPETITION_END_TIME=2024-09-27T23:59:59
MAX_TEAM_SIZE=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/ctf-arena/logs/ctf-arena.log
EOF

    echo "✅ Файл .env создан: $ENV_FILE"
    
    # Настраиваем права
    chown ctfapp:ctfapp "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    
    echo ""
    echo "⚠️  ВАЖНО: Отредактируйте файл .env для вашего окружения:"
    echo "   sudo nano $ENV_FILE"
    echo ""
    echo "Обязательные настройки:"
    echo "   - DATABASE_URL (если отличается от стандартной)"
    echo "   - SECRET_KEY (уже сгенерирован)"
    echo ""
    echo "Опциональные настройки:"
    echo "   - Email (для уведомлений)"
    echo "   - Telegram (для уведомлений)"
    echo "   - CORS_ORIGINS (для домена)"
    
else
    echo "✅ Файл .env уже существует: $ENV_FILE"
    echo "Проверьте его актуальность и при необходимости обновите."
fi

# Создаем директорию для логов
mkdir -p "$PROJECT_DIR/logs"
chown ctfapp:ctfapp "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"

echo ""
echo "🔧 Настройка окружения завершена!"
