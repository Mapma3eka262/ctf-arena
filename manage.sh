#!/bin/bash
# manage.sh

set -e

PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"

show_help() {
    echo "🚀 CyberCTF Arena Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services" 
    echo "  restart     - Restart all services"
    echo "  status      - Show services status"
    echo "  logs        - Show logs (all|api|websocket|celery)"
    echo "  backup      - Create database backup"
    echo "  update      - Update from git and restart"
    echo "  monitor     - Show real-time monitoring"
    echo "  shell       - Open Python shell"
    echo "  check       - Run system checks"
    echo "  help        - Show this help"
    echo ""
}

check_services() {
    echo "🔍 Проверка системы..."
    
    # Проверка директорий
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "❌ Проект не установлен в $PROJECT_DIR"
        return 1
    fi
    
    # Проверка .env файла
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        echo "❌ Файл .env не найден"
        return 1
    fi
    
    echo "✅ Базовая проверка пройдена"
    return 0
}

start_services() {
    echo "🚀 Запуск сервисов..."
    systemctl start ctf-api ctf-websocket ctf-celery ctf-celery-beat
    echo "✅ Сервисы запущены"
}

stop_services() {
    echo "🛑 Остановка сервисов..."
    systemctl stop ctf-api ctf-websocket ctf-celery ctf-celery-beat
    echo "✅ Сервисы остановлены"
}

restart_services() {
    echo "🔄 Перезапуск сервисов..."
    systemctl restart ctf-api ctf-websocket ctf-celery ctf-celery-beat
    echo "✅ Сервисы перезапущены"
}

show_status() {
    echo "📊 Статус сервисов:"
    echo ""
    
    services=("ctf-api" "ctf-websocket" "ctf-celery" "ctf-celery-beat" "nginx" "postgresql" "redis-server")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo "✅ $service: активен"
        else
            echo "❌ $service: неактивен"
        fi
    done
    
    echo ""
    echo "🌐 Проверка API..."
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ API: работает"
    else
        echo "❌ API: не отвечает"
    fi
    
    echo "🔗 Проверка WebSocket..."
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ WebSocket: работает"
    else
        echo "❌ WebSocket: не отвечает"
    fi
}

show_logs() {
    local service=${1:-"all"}
    
    case $service in
        "all")
            journalctl -u ctf-api -u ctf-websocket -u ctf-celery -f
            ;;
        "api")
            journalctl -u ctf-api -f
            ;;
        "websocket")
            journalctl -u ctf-websocket -f
            ;;
        "celery")
            journalctl -u ctf-celery -f
            ;;
        *)
            echo "❌ Неизвестный сервис: $service"
            echo "Доступные сервисы: all, api, websocket, celery"
            ;;
    esac
}

create_backup() {
    echo "💾 Создание бэкапа базы данных..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$PROJECT_DIR/backups/backup_$timestamp.sql"
    
    mkdir -p "$PROJECT_DIR/backups"
    
    sudo -u postgres pg_dump ctfarena > "$backup_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ Бэкап создан: $backup_file"
        
        # Очистка старых бэкапов (оставить последние 7)
        cd "$PROJECT_DIR/backups"
        ls -t backup_*.sql | tail -n +8 | xargs -r rm
        echo "🧹 Старые бэкапы очищены"
    else
        echo "❌ Ошибка создания бэкапа"
    fi
}

update_system() {
    echo "📥 Обновление системы..."
    
    # Остановка сервисов
    stop_services
    
    # Бэкап базы данных
    create_backup
    
    # Обновление кода (закомментируйте если не используете git)
    # cd "$PROJECT_DIR"
    # git pull origin main
    
    # Обновление зависимостей
    cd "$BACKEND_DIR"
    source venv/bin/activate
    pip install -r requirements/prod.txt
    
    # Применение миграций
    alembic upgrade head
    
    # Запуск сервисов
    start_services
    
    echo "✅ Система обновлена"
}

show_monitor() {
    echo "📈 Режим мониторинга (Ctrl+C для выхода)..."
    echo ""
    
    while true; do
        clear
        echo "🕐 $(date)"
        echo ""
        
        # Статус сервисов
        echo "🔧 Сервисы:"
        for service in ctf-api ctf-websocket ctf-celery; do
            if systemctl is-active --quiet "$service"; then
                echo "  ✅ $service"
            else
                echo "  ❌ $service"
            fi
        done
        
        echo ""
        
        # Использование ресурсов
        echo "💾 Ресурсы:"
        echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
        echo "  RAM: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
        echo "  Disk: $(df -h / | awk 'NR==2 {print $5}')"
        
        echo ""
        
        # Активные подключения
        echo "🔗 Подключения:"
        echo "  HTTP: $(netstat -an | grep :80 | wc -l)"
        echo "  WebSocket: $(netstat -an | grep :8001 | wc -l)"
        
        sleep 5
    done
}

open_shell() {
    echo "🐍 Запуск Python shell..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python -c "
import os
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge

db = SessionLocal()

print('🚀 CyberCTF Arena Python Shell')
print('Доступные объекты: db, User, Team, Challenge')
print('Пример: db.query(User).count()')

from IPython import embed
embed()
"
}

run_checks() {
    echo "🔍 Запуск проверок системы..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python check_structure.py
}

# Основная логика
case "${1:-}" in
    "start")
        check_services && start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        check_services && restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "backup")
        create_backup
        ;;
    "update")
        update_system
        ;;
    "monitor")
        show_monitor
        ;;
    "shell")
        open_shell
        ;;
    "check")
        run_checks
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo ""
        show_help
        exit 1
        ;;
esac