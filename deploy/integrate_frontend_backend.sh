#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/cyberctf/cyberctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
DB_NAME="cyberctf"
DB_USER="cyberctf"
DB_PASSWORD="cyberctf2024"

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

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        OS_ID=$ID
        OS_VERSION=$VERSION_ID
    else
        log_error "Cannot detect OS"
        exit 1
    fi
}

# Check if running as cyberctf user
check_user() {
    if [ "$(whoami)" != "cyberctf" ]; then
        log_error "This script must be run as 'cyberctf' user"
        log_info "Run: sudo -u cyberctf $0"
        exit 1
    fi
}

# Create project structure
create_structure() {
    log_info "Creating project structure..."
    
    mkdir -p $PROJECT_DIR
    mkdir -p $BACKEND_DIR/app
    mkdir -p $FRONTEND_DIR
    mkdir -p $BACKEND_DIR/migrations/versions
    mkdir -p $BACKEND_DIR/logs
    mkdir -p $BACKEND_DIR/static
    
    log_info "Project structure created"
}

# Setup Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    cd $BACKEND_DIR
    
    detect_os
    
    # Проверяем, существует ли виртуальная среда и работает ли
    if [ -d "$VENV_DIR" ]; then
        log_info "Virtual environment exists, testing..."
        source $VENV_DIR/bin/activate
        
        # Проверяем, установлен ли SQLAlchemy
        if ! python -c "import sqlalchemy" 2>/dev/null; then
            log_warn "Virtual environment exists but dependencies are missing. Reinstalling..."
            # Пересоздаем виртуальную среду
            rm -rf $VENV_DIR
            python3 -m venv $VENV_DIR
            source $VENV_DIR/bin/activate
        else
            log_info "Virtual environment is OK"
            return 0
        fi
    else
        # Создаем виртуальную среду
        log_info "Creating virtual environment..."
        python3 -m venv $VENV_DIR
        source $VENV_DIR/bin/activate
    fi
    
    # Обновляем pip
    log_info "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Устанавливаем зависимости в зависимости от ОС
    if [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        log_info "Installing CentOS-compatible dependencies..."
        python3 -m pip install \
            redis==4.5.0 \
            python-dateutil==2.8.2 \
            httpx==0.24.0 \
            aiofiles==22.1.0 \
            python-i18n==0.3.9 \
            email-validator==1.3.1 \
            pydantic==1.10.2 \
            pydantic-settings==2.0.3 \
            fastapi==0.95.2 \
            uvicorn==0.21.1 \
            python-multipart==0.0.6 \
            passlib[bcrypt]==1.7.4 \
            python-jose[cryptography]==3.3.0 \
            sqlalchemy==1.4.46 \
            alembic==1.10.2 \
            celery==5.2.7 \
            python-telegram-bot==20.3 \
            psycopg2-binary==2.9.6
    else
        log_info "Installing Ubuntu-compatible dependencies..."
        python3 -m pip install \
            redis==5.0.1 \
            python-dateutil==2.8.2 \
            httpx==0.25.2 \
            aiofiles==23.2.1 \
            python-i18n==0.3.9 \
            email-validator==2.1.0 \
            pydantic==2.5.0 \
            pydantic-settings==2.1.0 \
            fastapi==0.104.1 \
            uvicorn==0.24.0 \
            python-multipart==0.0.6 \
            passlib[bcrypt]==1.7.4 \
            python-jose[cryptography]==3.3.0 \
            sqlalchemy==2.0.23 \
            alembic==1.12.1 \
            celery==5.3.4 \
            python-telegram-bot==20.7 \
            psycopg2-binary==2.9.9
    fi
    
    # Проверяем ключевые зависимости
    log_info "Verifying key dependencies..."
    local key_deps=("sqlalchemy" "fastapi" "alembic" "psycopg2")
    for dep in "${key_deps[@]}"; do
        if python -c "import $dep" 2>/dev/null; then
            log_info "✓ $dep: OK"
        else
            log_error "✗ $dep: FAILED"
            return 1
        fi
    done
    
    log_info "Python environment setup completed"
}

# Configure environment variables
setup_environment() {
    log_info "Configuring environment variables..."
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    
    cat > $BACKEND_DIR/.env << EOF
# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (configure these in production)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@cyberctf.ru

# Telegram (configure these in production)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id

# Application
FRONTEND_URL=http://${SERVER_IP}
INVITATION_EXPIRE_HOURS=24

# Monitoring
SERVICE_CHECK_TIMEOUT=10
DEFAULT_CHECK_INTERVAL=3

# Competition
DEFAULT_PENALTY_MINUTES=30
MAX_TEAM_SIZE=5

# Languages
SUPPORTED_LANGUAGES=["ru", "en"]
DEFAULT_LANGUAGE=ru
EOF

    log_info "Environment configuration created"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    cd $BACKEND_DIR
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Run migrations
    if [ -f "$BACKEND_DIR/migrations/env.py" ]; then
        log_info "Running database migrations..."
        alembic upgrade head
    else
        log_warn "Migrations not found, creating initial tables..."
        python -c "
from app.core.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
    fi
    
    # Create initial admin user
    log_info "Creating initial admin user..."
    python -c "
import sys
sys.path.append('$BACKEND_DIR')
from app.core.database import SessionLocal
from app.models import User, Team
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Create admin team if not exists
    admin_team = db.query(Team).filter(Team.name == 'Administrators').first()
    if not admin_team:
        admin_team = Team(name='Administrators', score=0, is_active=True)
        db.add(admin_team)
        db.flush()

    # Create admin user if not exists
    admin_user = db.query(User).filter(User.username == 'admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@cyberctf.ru',
            password_hash=get_password_hash('admin123'),
            role='admin',
            team_id=admin_team.id,
            is_active=True,
            email_verified=True
        )
        db.add(admin_user)
        db.flush()
        
        # Set admin as team captain
        admin_team.captain_id = admin_user.id

    db.commit()
    print('Admin user created: username=admin, password=admin123')
except Exception as e:
    print(f'Error creating admin user: {e}')
    db.rollback()
finally:
    db.close()
"
    
    log_info "Database setup completed"
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."
    
    cd $FRONTEND_DIR
    
    # Check if package.json exists (for React/Vue projects)
    if [ -f "package.json" ]; then
        log_info "Installing frontend dependencies..."
        npm install || {
            log_warn "npm install failed, trying with --force"
            npm install --force
        }
        
        log_info "Building frontend..."
        npm run build || {
            log_error "Frontend build failed"
            return 1
        }
    else
        log_info "Using static HTML frontend"
        # Ensure frontend files are in place
        if [ ! -f "index.html" ]; then
            log_warn "No frontend files found. Please place HTML files in $FRONTEND_DIR"
            # Create basic index.html if missing
            cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberCTF Arena</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #1a1a1a; 
            color: white; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            text-align: center; 
        }
        h1 { color: #e00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CyberCTF Arena</h1>
        <p>Backend is running. Frontend files need to be deployed.</p>
        <p><a href="/lk.html" style="color: #e00;">Login</a> | <a href="/admin.html" style="color: #e00;">Admin</a></p>
    </div>
</body>
</html>
EOF
            log_info "Created basic index.html"
        fi
    fi
    
    log_info "Frontend build completed"
}

# Configure nginx for Ubuntu
setup_nginx_ubuntu() {
    log_info "Configuring nginx for Ubuntu..."
    
    # Create nginx configuration in sites-available
    sudo bash -c "cat > /etc/nginx/sites-available/cyberctf << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend static files
    location / {
        root $FRONTEND_DIR;
        try_files \\$uri \\$uri/ /index.html;
        index index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \\$host;
        access_log off;
    }
    
    # Static files for backend
    location /static/ {
        alias $BACKEND_DIR/static/;
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
}
EOF"
    
    # Enable site by creating symlink in sites-enabled
    sudo ln -sf /etc/nginx/sites-available/cyberctf /etc/nginx/sites-enabled/
    
    # Remove default site if exists
    if [ -f "/etc/nginx/sites-enabled/default" ]; then
        sudo rm /etc/nginx/sites-enabled/default
    fi
    
    log_info "Nginx configuration for Ubuntu completed"
}

# Configure nginx for CentOS
setup_nginx_centos() {
    log_info "Configuring nginx for CentOS..."
    
    # Create nginx configuration in conf.d directory
    sudo bash -c "cat > /etc/nginx/conf.d/cyberctf.conf << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend static files
    location / {
        root $FRONTEND_DIR;
        try_files \\$uri \\$uri/ /index.html;
        index index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \\$host;
        access_log off;
    }
    
    # Static files for backend
    location /static/ {
        alias $BACKEND_DIR/static/;
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
}
EOF"
    
    # Backup default nginx.conf and create custom one if needed
    if [ -f "/etc/nginx/nginx.conf" ]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi
    
    log_info "Nginx configuration for CentOS completed"
}

# Configure nginx based on OS
setup_nginx() {
    log_info "Configuring nginx for $OS..."
    
    detect_os
    
    case $OS_ID in
        ubuntu)
            setup_nginx_ubuntu
            ;;
        centos|rhel)
            setup_nginx_centos
            ;;
        *)
            log_error "Unsupported OS for nginx configuration: $OS"
            log_info "Please configure nginx manually"
            return 1
            ;;
    esac
    
    # Test nginx configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        sudo systemctl enable nginx
        log_info "Nginx configuration test passed and reloaded"
    else
        log_error "Nginx configuration test failed"
        return 1
    fi
}

# Create systemd services
create_services() {
    log_info "Creating systemd services..."
    
    # Backend service
    sudo bash -c "cat > /etc/systemd/system/cyberctf-backend.service << EOF
[Unit]
Description=CyberCTF Arena Backend
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=cyberctf
Group=cyberctf
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"
    
    # Celery worker service
    sudo bash -c "cat > /etc/systemd/system/cyberctf-celery.service << EOF
[Unit]
Description=CyberCTF Arena Celery Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=cyberctf
Group=cyberctf
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/celery -A app.tasks.celery worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"
    
    # Celery beat service
    sudo bash -c "cat > /etc/systemd/system/cyberctf-celerybeat.service << EOF
[Unit]
Description=CyberCTF Arena Celery Beat
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=cyberctf
Group=cyberctf
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/celery -A app.tasks.celery beat --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"
    
    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable cyberctf-backend cyberctf-celery cyberctf-celerybeat
    
    log_info "Systemd services created"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Start backend services
    sudo systemctl start cyberctf-backend
    sudo systemctl start cyberctf-celery
    sudo systemctl start cyberctf-celerybeat
    
    # Wait a bit for services to start
    sleep 5
    
    # Check service status
    log_info "Service status:"
    if sudo systemctl is-active cyberctf-backend >/dev/null; then
        log_info "✓ Backend service: ACTIVE"
    else
        log_error "✗ Backend service: FAILED"
        sudo systemctl status cyberctf-backend --no-pager
        return 1
    fi
    
    if sudo systemctl is-active cyberctf-celery >/dev/null; then
        log_info "✓ Celery worker service: ACTIVE"
    else
        log_error "✗ Celery worker service: FAILED"
        sudo systemctl status cyberctf-celery --no-pager
    fi
    
    if sudo systemctl is-active cyberctf-celerybeat >/dev/null; then
        log_info "✓ Celery beat service: ACTIVE"
    else
        log_error "✗ Celery beat service: FAILED"
        sudo systemctl status cyberctf-celerybeat --no-pager
    fi
    
    return 0
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    sleep 10
    
    local health_checks_passed=0
    local total_checks=3
    
    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "✓ Backend health check: PASSED"
        ((health_checks_passed++))
    else
        log_error "✗ Backend health check: FAILED"
        log_info "Trying to get more details..."
        curl -v http://localhost:8000/health || true
    fi
    
    # Check nginx
    if curl -f http://localhost >/dev/null 2>&1; then
        log_info "✓ Nginx health check: PASSED"
        ((health_checks_passed++))
    else
        log_error "✗ Nginx health check: FAILED"
    fi
    
    # Check database connection
    cd $BACKEND_DIR
    source $VENV_DIR/bin/activate
    if python -c "
import sys
sys.path.append('$BACKEND_DIR')
from app.core.database import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log_info "✓ Database connection: PASSED"
        ((health_checks_passed++))
    else
        log_error "✗ Database connection: FAILED"
    fi
    
    if [ $health_checks_passed -eq $total_checks ]; then
        log_info "🎉 All health checks passed! System is ready."
        return 0
    else
        log_warn "Only $health_checks_passed out of $total_checks health checks passed"
        return 1
    fi
}

# Create management script
create_management_script() {
    log_info "Creating management script..."
    
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
        echo "=== Service Status ==="
        sudo systemctl status cyberctf-backend --no-pager
        echo ""
        sudo systemctl status cyberctf-celery --no-pager
        echo ""
        sudo systemctl status cyberctf-celerybeat --no-pager
        ;;
    logs)
        sudo journalctl -u cyberctf-backend -f
        ;;
    celery-logs)
        sudo journalctl -u cyberctf-celery -f
        ;;
    nginx-logs)
        sudo tail -f /var/log/nginx/access.log
        ;;
    nginx-error-logs)
        sudo tail -f /var/log/nginx/error.log
        ;;
    backup)
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_file="/home/cyberctf/backups/cyberctf_${timestamp}.backup"
        mkdir -p /home/cyberctf/backups
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
print('Example: users = db.query(User).all()')
"
        ;;
    health)
        curl -f http://localhost:8000/health && echo "Backend: HEALTHY" || echo "Backend: UNHEALTHY"
        curl -f http://localhost && echo "Nginx: HEALTHY" || echo "Nginx: UNHEALTHY"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|celery-logs|nginx-logs|nginx-error-logs|backup|update|shell|health}"
        echo ""
        echo "Commands:"
        echo "  start     - Start all services"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Show detailed service status"
        echo "  logs      - Show backend logs (follow)"
        echo "  celery-logs - Show celery logs (follow)"
        echo "  nginx-logs - Show nginx access logs (follow)"
        echo "  nginx-error-logs - Show nginx error logs (follow)"
        echo "  backup    - Create database backup"
        echo "  update    - Update application"
        echo "  shell     - Open database shell"
        echo "  health    - Quick health check"
        exit 1
        ;;
esac
EOF
    
    chmod +x $PROJECT_DIR/manage.sh
    log_info "Management script created: $PROJECT_DIR/manage.sh"
}

# Display final information
display_info() {
    log_info "=== CyberCTF Arena Integration Complete ==="
    echo ""
    SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    echo "🌐 Application URLs:"
    echo "   Main Site:    http://${SERVER_IP}"
    echo "   Login:        http://${SERVER_IP}/lk.html"
    echo "   Arena:        http://${SERVER_IP}/arena.html"
    echo "   Admin Panel:  http://${SERVER_IP}/admin.html"
    echo "   API Docs:     http://${SERVER_IP}/docs"
    echo ""
    echo "🔑 Default Admin Credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo "   Email:    admin@cyberctf.ru"
    echo ""
    echo "⚙️  Management Commands:"
    echo "   cd $PROJECT_DIR"
    echo "   ./manage.sh status    # Check service status"
    echo "   ./manage.sh logs      # View backend logs"
    echo "   ./manage.sh health    # Quick health check"
    echo ""
    echo "📊 Service Status:"
    sudo systemctl is-active cyberctf-backend >/dev/null && echo "   Backend:   ✅ Running" || echo "   Backend:   ❌ Stopped"
    sudo systemctl is-active cyberctf-celery >/dev/null && echo "   Celery:    ✅ Running" || echo "   Celery:    ❌ Stopped"
    sudo systemctl is-active nginx >/dev/null && echo "   Nginx:     ✅ Running" || echo "   Nginx:     ❌ Stopped"
    sudo systemctl is-active postgresql >/dev/null && echo "   PostgreSQL:✅ Running" || echo "   PostgreSQL:❌ Stopped"
    sudo systemctl is-active redis >/dev/null 2>/dev/null && echo "   Redis:     ✅ Running" || sudo systemctl is-active redis-server >/dev/null && echo "   Redis:     ✅ Running" || echo "   Redis:     ❌ Stopped"
    echo ""
    echo "🚨 Important Next Steps:"
    echo "   1. Change default admin password"
    echo "   2. Configure email settings in $BACKEND_DIR/.env"
    echo "   3. Set up SSL certificate for production"
    echo "   4. Configure backup strategy"
    echo ""
}

# Main execution
main() {
    log_info "Starting backend-frontend integration..."
    
    detect_os
    log_info "Detected OS: $OS $OS_VERSION"
    
    check_user
    
    # Check if project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        log_info "Please deploy the project files first"
        exit 1
    fi
    
    # Create basic structure if missing
    create_structure
    
    setup_python_env || {
        log_error "Python environment setup failed"
        exit 1
    }
    
    setup_environment
    setup_database
    build_frontend
    setup_nginx
    create_services
    start_services || {
        log_error "Failed to start services"
        exit 1
    }
    health_check
    create_management_script
    display_info
    
    log_info "🎉 Backend-frontend integration completed successfully!"
    log_info ""
    log_info "The CyberCTF Arena is now ready for use!"
}

# Run main function
main "$@"
