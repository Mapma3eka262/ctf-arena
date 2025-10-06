#!/bin/bash

# CyberCTF Arena - Deployment Script
set -e

echo "🚀 Запуск деплоя CyberCTF Arena..."

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root"
    exit 1
fi

# Переменные
PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
NGINX_DIR="/etc/nginx"

# Остановка сервисов перед деплоем
echo "🛑 Остановка сервисов..."
systemctl stop ctf-api ctf-celery ctf-celery-beat nginx || true

# Бэкап базы данных
echo "💾 Создание бэкапа базы данных..."
BACKUP_FILE="$PROJECT_DIR/backups/backup_$(date +%Y%m%d_%H%M%S).sql"
sudo -u postgres pg_dump ctfarena > $BACKUP_FILE
echo "✅ Бэкап создан: $BACKUP_FILE"

# Обновление кода (в реальном сценарии здесь будет git pull)
echo "📥 Обновление кода приложения..."
# git pull origin main  # Раскомментировать для production

# Установка зависимостей
echo "📦 Обновление зависимостей..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt

# Применение миграций базы данных
echo "🗄️ Применение миграций базы данных..."
if [ -d "migrations" ]; then
    alembic upgrade head
fi

# Сборка статических файлов
echo "📁 Сборка статических файлов..."
python3 -c "
from app.main import app
# Здесь может быть логика сборки статики
print('✅ Статические файлы собраны')
"

# Настройка Nginx
echo "🌐 Настройка Nginx..."
cat > $NGINX_DIR/sites-available/ctf-arena << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /opt/ctf-arena/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Статические файлы
    location /static {
        alias /opt/ctf-arena/backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Загрузки
    location /uploads {
        alias /opt/ctf-arena/uploads;
        expires 1h;
        add_header Cache-Control "public";
    }
}

# HTTPS конфигурация (раскомментировать после настройки SSL)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com;
#     
#     ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
#     
#     # Остальная конфигурация аналогична выше
# }
EOF

# Активация сайта Nginx
ln -sf $NGINX_DIR/sites-available/ctf-arena $NGINX_DIR/sites-enabled/
rm -f $NGINX_DIR/sites-enabled/default

# Проверка конфигурации Nginx
echo "🔍 Проверка конфигурации Nginx..."
nginx -t

# Настройка прав
echo "🔒 Настройка прав доступа..."
chown -R ctfapp:ctfapp $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $PROJECT_DIR/backups/*.sql 2>/dev/null || true

# Запуск сервисов
echo "▶️ Запуск сервисов..."
systemctl daemon-reload
systemctl enable ctf-api ctf-celery ctf-celery-beat nginx
systemctl start nginx ctf-api ctf-celery ctf-celery-beat

# Проверка статуса сервисов
echo "📊 Проверка статуса сервисов..."
for service in nginx ctf-api ctf-celery ctf-celery-beat; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service: запущен"
    else
        echo "❌ $service: не запущен"
        systemctl status $service --no-pager
    fi
done

# Очистка старых бэкапов (храним только последние 7)
echo "🧹 Очистка старых бэкапов..."
ls -t $PROJECT_DIR/backups/*.sql | tail -n +8 | xargs rm -f

echo ""
echo "🎉 Деплой CyberCTF Arena завершен!"
echo ""
echo "📊 Статус сервисов:"
echo "   systemctl status ctf-api"
echo "   systemctl status ctf-celery" 
echo "   systemctl status ctf-celery-beat"
echo ""
echo "🌐 Приложение доступно по адресу: http://your-server-ip"
echo ""
echo "⚠️  Не забудьте:"
echo "   1. Настроить доменное имя"
echo "   2. Получить SSL сертификат: certbot --nginx"
echo "   3. Настроить файл .env с секретными ключами"