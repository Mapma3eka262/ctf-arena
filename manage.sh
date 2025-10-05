#!/bin/bash

# CyberCTF Arena Management Script

PROJECT_DIR="/home/cyberctf/cyberctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"

case "$1" in
    start)
        sudo systemctl start cyberctf-backend cyberctf-celery cyberctf-celerybeat
        echo "Services started"
        ;;
    stop)
        sudo systemctl stop cyberctf-backend cyberctf-celery cyberctf-celerybeat
        echo "Services stopped"
        ;;
    restart)
        sudo systemctl restart cyberctf-backend cyberctf-celery cyberctf-celerybeat
        echo "Services restarted"
        ;;
    status)
        sudo systemctl status cyberctf-backend cyberctf-celery cyberctf-celerybeat
        ;;
    logs)
        sudo journalctl -u cyberctf-backend -f
        ;;
    celery-logs)
        sudo journalctl -u cyberctf-celery -f
        ;;
    backup)
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_file="/home/cyberctf/backups/cyberctf_${timestamp}.backup"
        sudo -u postgres pg_dump cyberctf > $backup_file
        echo "Backup created: $backup_file"
        ;;
    update)
        cd $PROJECT_DIR
        git pull
        cd backend
        source venv/bin/activate
        alembic upgrade head
        sudo systemctl restart cyberctf-backend cyberctf-celery cyberctf-celerybeat
        echo "Application updated"
        ;;
    shell)
        cd $BACKEND_DIR
        source venv/bin/activate
        python -c "
from app.core.database import SessionLocal
from app.models import User, Team, Challenge
db = SessionLocal()
print('Database shell ready. Available objects: db, User, Team, Challenge')
"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|celery-logs|backup|update|shell}"
        echo ""
        echo "Commands:"
        echo "  start     - Start all services"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Show service status"
        echo "  logs      - Show backend logs"
        echo "  celery-logs - Show celery logs"
        echo "  backup    - Create database backup"
        echo "  update    - Update application"
        echo "  shell     - Open database shell"
        exit 1
        ;;
esac
