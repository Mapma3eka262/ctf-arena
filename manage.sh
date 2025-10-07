#!/bin/bash

# CyberCTF Arena - Management Script for Ubuntu 24.04

PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_PATH="$BACKEND_DIR/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Этот скрипт требует прав root. Используйте: sudo $0 $1"
        exit 1
    fi
}

check_service_exists() {
    local service=$1
    if [ ! -f "/etc/systemd/system/$service" ]; then
        log_error "Сервис $service не найден. Сначала запустите интеграцию."
        return 1
    fi
    return 0
}

# Commands
case "$1" in
    "start")
        check_root "start"
        log_info "Запуск CyberCTF Arena..."
        
        for service in ctf-api ctf-celery ctf-celery-beat nginx; do
            if check_service_exists "$service.service"; then
                systemctl start $service
                log_success "Сервис $service запущен"
            fi
        done
        ;;
        
    "stop")
        check_root "stop"
        log_info "Остановка CyberCTF Arena..."
        
        for service in ctf-api ctf-celery ctf-celery-beat nginx; do
            if systemctl is-active --quiet $service 2>/dev/null; then
                systemctl stop $service
                log_success "Сервис $service остановлен"
            fi
        done
        ;;
        
    "restart")
        check_root "restart"
        log_info "Перезапуск CyberCTF Arena..."
        
        for service in ctf-api ctf-celery ctf-celery-beat nginx; do
            if check_service_exists "$service.service"; then
                systemctl restart $service
                log_success "Сервис $service перезапущен"
            fi
        done
        ;;
        
    "status")
        log_info "Статус сервисов CyberCTF Arena:"
        echo "=== Основные сервисы ==="
        for service in nginx ctf-api ctf-celery ctf-celery-beat; do
            if systemctl is-active --quiet $service 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} $service: запущен"
            else
                echo -e "  ${RED}✗${NC} $service: остановлен"
            fi
        done
        
        echo "=== Системные сервисы ==="
        for service in postgresql redis-server fail2ban; do
            if systemctl is-active --quiet $service; then
                echo -e "  ${GREEN}✓${NC} $service: запущен"
            else
                echo -e "  ${YELLOW}⚠${NC} $service: остановлен"
            fi
        done
        ;;
        
    "logs")
        service=${2:-"ctf-api"}
        if ! check_service_exists "$service.service"; then
            exit 1
        fi
        log_info "Логи сервиса $service:"
        journalctl -u $service -f --lines=50
        ;;
        
    "setup-db")
        check_root "setup-db"
        log_info "Настройка базы данных..."
        
        cd $BACKEND_DIR
        source $VENV_PATH/bin/activate
        export PYTHONPATH="$BACKEND_DIR"
        
        python3 -c "
import sys
sys.path.append('$BACKEND_DIR')
try:
    from app.core.database import init_db
    from app.core.config import settings
    init_db()
    print('✅ База данных инициализирована')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    sys.exit(1)
        " || exit 1
        ;;
        
    "backup")
        check_root "backup"
        log_info "Создание бэкапа базы данных..."
        BACKUP_FILE="$PROJECT_DIR/backups/backup_$(date +%Y%m%d_%H%M%S).sql"
        sudo -u postgres pg_dump ctfarena > $BACKUP_FILE 2>/dev/null || {
            log_error "Не удалось создать бэкап. Проверьте доступ к PostgreSQL."
            exit 1
        }
        log_success "Бэкап создан: $BACKUP_FILE ($(du -h $BACKUP_FILE | cut -f1))"
        ;;
        
    "restore")
        check_root "restore"
        if [ -z "$2" ]; then
            log_error "Укажите файл бэкапа: $0 restore /path/to/backup.sql"
            exit 1
        fi
        log_info "Восстановление базы данных из $2..."
        sudo -u postgres psql -d ctfarena -f "$2"
        log_success "База данных восстановлена"
        ;;
        
    "update")
        check_root "update"
        log_info "Обновление CyberCTF Arena..."
        
        # Остановка сервисов
        $0 stop
        
        # Бэкап
        $0 backup
        
        # Обновление кода (в production здесь будет git pull)
        log_info "Обновление кода..."
        cd $PROJECT_DIR
        # git pull origin main
        
        # Обновление зависимостей
        log_info "Обновление зависимостей..."
        cd $BACKEND_DIR
        activate_venv
        pip install -r requirements.txt
        
        # Миграции базы данных
        log_info "Применение миграций..."
        alembic upgrade head
        
        # Запуск сервисов
        $0 start
        
        log_success "Обновление завершено"
        ;;
        
    "monitor")
        log_info "Мониторинг системы:"
        echo "--- Память ---"
        free -h
        echo ""
        echo "--- Диск ---"
        df -h
        echo ""
        echo "--- Сетевые соединения ---"
        netstat -tulpn | grep -E ':(80|443|8000|5432|6379)'
        ;;
        
    "cleanup")
        check_root "cleanup"
        log_info "Очистка системы..."
        
        # Очистка логов
        journalctl --vacuum-time=7d
        
        # Очистка старых бэкапов
        find $PROJECT_DIR/backups -name "*.sql" -mtime +30 -delete
        
        # Очистка кэша
        apt autoremove -y
        apt autoclean
        
        log_success "Очистка завершена"
        ;;
        
    "quick-install")
        check_root "quick-install"
        log_info "Быстрая установка CyberCTF Arena..."
        
        # Запуск всех скриптов установки
        ./deploy/setup_server.sh
        ./deploy/integrate_frontend_backend.sh
        ./deploy/deploy_project.sh
        
        log_success "Установка завершена!"
        ;;
        
    *)
        echo "CyberCTF Arena Management Script для Ubuntu 24.04"
        echo ""
        echo "Использование: $0 {команда}"
        echo ""
        echo "Команды:"
        echo "  start           - Запуск всех сервисов"
        echo "  stop            - Остановка всех сервисов" 
        echo "  restart         - Перезапуск всех сервисов"
        echo "  status          - Статус сервисов"
        echo "  logs [service]  - Просмотр логов сервиса"
        echo "  setup-db        - Инициализация базы данных"
        echo "  backup          - Создание бэкапа БД"
        echo "  restore <file>  - Восстановление БД из файла"
        echo "  update          - Обновление приложения"
        echo "  monitor         - Мониторинг системы"
        echo "  cleanup         - Очистка системы"
        echo ""
        echo "Примеры:"
        echo "  sudo $0 start"
        echo "  sudo $0 status"
        echo "  sudo $0 setup-db"
        ;;
esac
