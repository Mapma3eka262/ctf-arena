#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cyberctf-arena"
PROJECT_DIR="/home/cyberctf/$PROJECT_NAME"
GIT_REPO="https://github.com/Mapma3eka262/cyberctf-arena.git"
BACKUP_DIR="/home/cyberctf/backups"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as cyberctf user
check_user() {
    if [ "$(whoami)" != "cyberctf" ]; then
        log_error "This script must be run as 'cyberctf' user"
        log_info "Run: sudo -u cyberctf $0"
        exit 1
    fi
}

# Create backup
create_backup() {
    log_info "Creating backup..."
    
    mkdir -p $BACKUP_DIR
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/${PROJECT_NAME}_${timestamp}.tar.gz"
    
    if [ -d "$PROJECT_DIR" ]; then
        tar -czf $backup_file -C /home/cyberctf $PROJECT_NAME
        log_info "Backup created: $backup_file"
    else
        log_warn "No existing project to backup"
    fi
}

# Clone or update project
deploy_project() {
    log_info "Deploying project..."
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        log_info "Updating existing repository..."
        cd $PROJECT_DIR
        git pull
    else
        log_info "Cloning repository..."
        if [ -n "$GIT_REPO" ] && [ "$GIT_REPO" != "https://github.com/Mapma3eka262/cyberctf-arena.git" ]; then
            git clone $GIT_REPO $PROJECT_DIR
        else
            log_error "Please set GIT_REPO variable in the script"
            log_info "Or manually place project files in $PROJECT_DIR"
            exit 1
        fi
    fi
    
    # Set proper permissions
    chmod -R 755 $PROJECT_DIR
    chmod 600 $PROJECT_DIR/backend/.env 2>/dev/null || true
}

# Setup project structure
setup_project() {
    log_info "Setting up project structure..."
    
    # Ensure directories exist
    mkdir -p $PROJECT_DIR/backend/logs
    mkdir -p $PROJECT_DIR/backend/static
    mkdir -p $PROJECT_DIR/frontend
    
    # Create necessary files if they don't exist
    if [ ! -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        cat > $PROJECT_DIR/backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
celery==5.3.4
python-telegram-bot==20.7
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0
python-i18n==0.3.9
httpx==0.25.2
aiofiles==23.2.1
python-dateutil==2.8.2
EOF
    fi
    
    # Create docker-compose file for development
    if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
        cat > $PROJECT_DIR/docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cyberctf:cyberctf2024@db:5432/cyberctf
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./frontend:/app/frontend
      - ./backend/app:/app/app
      - ./backend/logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=cyberctf
      - POSTGRES_USER=cyberctf
      - POSTGRES_PASSWORD=cyberctf2024
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend

volumes:
  postgres_data:
EOF
    fi
    
    # Create backend Dockerfile
    if [ ! -f "$PROJECT_DIR/backend/Dockerfile" ]; then
        cat > $PROJECT_DIR/backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd $PROJECT_DIR/backend
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        if command -v alembic >/dev/null 2>&1; then
            alembic upgrade head
            log_info "Database migrations completed"
        else
            log_warn "Alembic not found, creating initial tables..."
            python -c "
from app.core.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Initial tables created')
"
        fi
    else
        log_error "Virtual environment not found"
        return 1
    fi
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Stop services if running
    sudo systemctl stop cyberctf-backend cyberctf-celery cyberctf-celerybeat 2>/dev/null || true
    
    # Start services
    sudo systemctl start cyberctf-backend
    sudo systemctl start cyberctf-celery
    sudo systemctl start cyberctf-celerybeat
    
    # Wait a bit for services to start
    sleep 5
    
    # Check service status
    log_info "Service status:"
    sudo systemctl is-active cyberctf-backend && log_info "Backend: ACTIVE" || log_error "Backend: FAILED"
    sudo systemctl is-active cyberctf-celery && log_info "Celery Worker: ACTIVE" || log_error "Celery Worker: FAILED"
    sudo systemctl is-active cyberctf-celerybeat && log_info "Celery Beat: ACTIVE" || log_error "Celery Beat: FAILED"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "Backend health check: PASSED"
    else
        log_error "Backend health check: FAILED"
        return 1
    fi
    
    # Check nginx
    if curl -f http://localhost >/dev/null 2>&1; then
        log_info "Nginx health check: PASSED"
    else
        log_error "Nginx health check: FAILED"
        return 1
    fi
    
    # Check database connection
    cd $PROJECT_DIR/backend
    source venv/bin/activate
    if python -c "
from app.core.database import SessionLocal
db = SessionLocal()
db.execute('SELECT 1')
db.close()
print('Database connection: OK')
" 2>/dev/null; then
        log_info "Database connection: PASSED"
    else
        log_error "Database connection: FAILED"
        return 1
    fi
}

# Create admin script
create_admin_script() {
    log_info "Creating admin management script..."
    
    cat > $PROJECT_DIR/manage.sh << 'EOF'
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
EOF
    
    chmod +x $PROJECT_DIR/manage.sh
    log_info "Management script created: $PROJECT_DIR/manage.sh"
}

# Display final information
display_info() {
    log_info "=== CyberCTF Arena Deployment Complete ==="
    echo ""
    echo "📋 Application Information:"
    echo "   URL: http://$(curl -s ifconfig.me)"
    echo "   Admin Panel: http://$(curl -s ifconfig.me)/admin.html"
    echo "   API Documentation: http://$(curl -s ifconfig.me)/docs"
    echo ""
    echo "🔑 Default Admin Credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "⚙️ Management Commands:"
    echo "   Start/Stop: $PROJECT_DIR/manage.sh {start|stop|restart}"
    echo "   View logs: $PROJECT_DIR/manage.sh logs"
    echo "   Status: $PROJECT_DIR/manage.sh status"
    echo "   Backup: $PROJECT_DIR/manage.sh backup"
    echo ""
    echo "📊 Service Status:"
    sudo systemctl is-active cyberctf-backend >/dev/null && echo "   Backend: ✅ Running" || echo "   Backend: ❌ Stopped"
    sudo systemctl is-active cyberctf-celery >/dev/null && echo "   Celery: ✅ Running" || echo "   Celery: ❌ Stopped"
    sudo systemctl is-active nginx >/dev/null && echo "   Nginx: ✅ Running" || echo "   Nginx: ❌ Stopped"
    echo ""
    echo "🚨 Security Recommendations:"
    echo "   1. Change default admin password"
    echo "   2. Configure SSL certificate"
    echo "   3. Update email and Telegram settings in .env"
    echo "   4. Configure firewall rules"
    echo ""
}

# Main execution
main() {
    log_info "Starting CyberCTF Arena deployment..."
    
    check_user
    create_backup
    deploy_project
    setup_project
    
    # Run integration script
    log_info "Running integration..."
    bash $(dirname "$0")/integrate_frontend_backend.sh
    
    run_migrations
    start_services
    health_check
    create_admin_script
    display_info
    
    log_info "🎉 Deployment completed successfully!"
    log_info "The CyberCTF Arena is now ready for use."
}

# Run main function
main "$@"
