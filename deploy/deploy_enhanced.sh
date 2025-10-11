#!/bin/bash
# deploy/deploy_enhanced.sh

set -e

echo "🚀 Запуск улучшенного деплоя CyberCTF Arena..."

# Переменные
PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root: sudo ./deploy_enhanced.sh"
    exit 1
fi

# Остановка существующих сервисов
echo "🛑 Остановка сервисов..."
docker-compose -f $PROJECT_DIR/docker-compose.microservices.yml down || true
systemctl stop ctf-api ctf-websocket ctf-dynamic || true

# Бэкап базы данных
echo "💾 Создание бэкапа базы данных..."
BACKUP_FILE="$PROJECT_DIR/backups/backup_$(date +%Y%m%d_%H%M%S).sql"
sudo -u postgres pg_dump ctfarena > $BACKUP_FILE 2>/dev/null || {
    echo "⚠️  Не удалось создать бэкап (возможно, база данных пустая)"
}

# Обновление кода
echo "📥 Обновление кода..."
cd $PROJECT_DIR
# git pull origin main  # Раскомментировать для production

# Настройка окружения
echo "⚙️  Настройка окружения..."
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "✅ Файл .env уже существует"
else
    cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env
    echo "⚠️  Создан файл .env из примера. Отредактируйте его!"
fi

# Сборка Docker образов
echo "🐳 Сборка Docker образов..."
cd $PROJECT_DIR
docker-compose -f docker-compose.microservices.yml build

# Запуск микросервисов
echo "🚀 Запуск микросервисов..."
docker-compose -f docker-compose.microservices.yml up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 30

# Применение миграций
echo "🗄️ Применение миграций базы данных..."
cd $BACKEND_DIR
docker-compose -f ../docker-compose.microservices.yml exec ctf-api alembic upgrade head

# Инициализация динамических заданий
echo "🎯 Инициализация динамических заданий..."
docker-compose -f ../docker-compose.microservices.yml exec ctf-api python -c "
import asyncio
import sys
sys.path.append('/app')
from app.core.database import init_db
from app.utils.init_dynamic_challenges import init_dynamic_challenges

init_db()
asyncio.run(init_dynamic_challenges())
print('✅ Динамические задания инициализированы')
"

# Настройка прав
echo "🔒 Настройка прав доступа..."
chown -R ctfapp:ctfapp $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $PROJECT_DIR/backups/*.sql 2>/dev/null || true

# Проверка статуса сервисов
echo "📊 Проверка статуса сервисов..."
services=("ctf-api" "ctf-websocket" "ctf-dynamic" "postgres" "redis" "nginx")
for service in "${services[@]}"; do
    if docker-compose -f docker-compose.microservices.yml ps | grep -q "$service.*Up"; then
        echo "✅ $service: запущен"
    else
        echo "❌ $service: не запущен"
    fi
done

# Очистка старых бэкапов
echo "🧹 Очистка старых бэкапов..."
find $PROJECT_DIR/backups -name "*.sql" -mtime +7 -delete

echo ""
echo "🎉 Улучшенный деплой CyberCTF Arena завершен!"
echo ""
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.microservices.yml ps
echo ""
echo "🌐 Приложение доступно по адресу: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "⚠️  Не забудьте:"
echo "   1. Проверить настройки в файле $PROJECT_DIR/.env"
echo "   2. Настроить SSL сертификаты"
echo "   3. Настроить брандмауэр"
echo "   4. Настроить мониторинг"