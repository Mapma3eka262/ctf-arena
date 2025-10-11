#!/bin/bash
# deploy/deploy_project.sh

set -e

echo "🚀 Деплой проекта CyberCTF Arena..."

PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root: sudo ./deploy_project.sh"
    exit 1
fi

# Остановка сервисов
echo "🛑 Остановка сервисов..."
systemctl stop ctf-api ctf-websocket ctf-celery ctf-celery-beat || true

# Создание виртуального окружения Python
echo "🐍 Настройка Python окружения..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Активация venv и установка зависимостей
source venv/bin/activate

echo "📦 Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements/prod.txt

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."

# Проверка структуры проекта
python check_structure.py

# Простая инициализация БД
python simple_init_db.py

# Применение миграций Alembic (если есть)
if [ -f "alembic.ini" ]; then
    echo "🔄 Применение миграций Alembic..."
    alembic upgrade head
fi

# Настройка прав
echo "🔒 Настройка прав доступа..."
chown -R ctfapp:ctfapp "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
chmod 750 "$PROJECT_DIR/backups"
chmod 755 "$PROJECT_DIR/uploads"

# Создание директории для логов
mkdir -p /var/log/ctf-arena
chown ctfapp:ctfapp /var/log/ctf-arena

# Запуск сервисов
echo "🚀 Запуск сервисов..."
systemctl start ctf-api ctf-websocket ctf-celery ctf-celery-beat
systemctl enable ctf-api ctf-websocket ctf-celery ctf-celery-beat

# Проверка статуса сервисов
echo "📊 Проверка статуса сервисов..."
services=("ctf-api" "ctf-websocket" "ctf-celery" "ctf-celery-beat" "nginx" "postgresql" "redis-server")

for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✅ $service: запущен"
    else
        echo "❌ $service: не запущен"
    fi
done

# Проверка здоровья API
echo "🔍 Проверка здоровья API..."
sleep 10  # Даем время сервисам запуститься

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API работает корректно"
else
    echo "❌ API не отвечает"
fi

# Проверка WebSocket
echo "🔍 Проверка WebSocket..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ WebSocket работает корректно"
else
    echo "❌ WebSocket не отвечает"
fi

echo ""
echo "🎉 Деплой CyberCTF Arena завершен!"
echo ""
echo "🌐 Приложение доступно по адресам:"
echo "   - HTTP: http://$(curl -s ifconfig.me)"
echo "   - Локально: http://localhost"
echo ""
echo "👤 Тестовый аккаунт:"
echo "   - Логин: admin"
echo "   - Пароль: admin123"
echo ""
echo "📝 Дополнительные действия:"
echo "   - Настройте доменное имя и SSL"
echo "   - Настройте мониторинг"
echo "   - Настройте резервное копирование"
echo "   - Добавьте задания и настройте соревнование"