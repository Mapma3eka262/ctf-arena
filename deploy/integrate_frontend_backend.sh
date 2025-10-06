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
    
    log_info "Project structure created"
}

# Setup Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    cd $BACKEND_DIR
    
    # Create virtual environment
    python3 -m venv $VENV_DIR
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_warn "requirements.txt not found, installing default dependencies"
        pip install \
            fastapi==0.104.1 \
            uvicorn==0.24.0 \
            sqlalchemy==2.0.23 \
            psycopg2-binary==2.9.9 \
            alembic==1.12.1 \
            python-jose[cryptography]==3.3.0 \
            passlib[bcrypt]==1.7.4 \
            python-multipart==0.0.6 \
            redis==5.0.1 \
            celery==5.3.4 \
            python-telegram-bot==20.7 \
            pydantic==2.5.0 \
            pydantic-settings==2.1.0 \
            email-validator==2.1.0 \
            python-i18n==0.3.9 \
            httpx==0.25.2 \
            aiofiles==23.2.1 \
            python-dateutil==2.8.2
    fi

    # Проверка установки ключевых зависимостей
    log_info "Checking key dependencies..."
    if ! python -c "import sqlalchemy; print('SQLAlchemy OK')" 2>/dev/null; then
        log_error "SQLAlchemy not installed properly"
        exit 1
    fi
    
    if ! python -c "import fastapi; print('FastAPI OK')" 2>/dev/null; then
        log_error "FastAPI not installed properly"
        exit 1
    fi
    
    log_info "Python environment setup completed"
}

# Configure environment variables
setup_environment() {
    log_info "Configuring environment variables..."
    
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
FRONTEND_URL=http://localhost:3000
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
db.close()
print('Admin user created: username=admin, password=admin123')
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
        npm install
        
        log_info "Building frontend..."
        npm run build
    else
        log_info "Using static HTML frontend"
        # Ensure frontend files are in place
        if [ ! -f "index.html" ]; then
            log_warn "No frontend files found. Please place HTML files in $FRONTEND_DIR"
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
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \\$host;
    }
    
    # Static files for backend
    location /static/ {
        alias $BACKEND_DIR/static/;
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
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host \\$host;
    }
    
    # Static files for backend
    location /static/ {
        alias $BACKEND_DIR/static/;
    }
}
EOF"
    
    # Backup default nginx.conf and create custom one
    if [ -f "/etc/nginx/nginx.conf" ]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi
    
    # Create custom nginx.conf for CentOS
    sudo bash -c "cat > /etc/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] \"\$request\" '
                      '\$status \$body_bytes_sent \"\$http_referer\" '
                      '\"\$http_user_agent\" \"\$http_x_forwarded_for\"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;
}
EOF"
    
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
    sleep 3
    
    # Check service status
    log_info "Service status:"
    if sudo systemctl is-active cyberctf-backend >/dev/null; then
        log_info "Backend service: ACTIVE"
    else
        log_error "Backend service: FAILED"
        sudo systemctl status cyberctf-backend --no-pager
    fi
    
    if sudo systemctl is-active cyberctf-celery >/dev/null; then
        log_info "Celery worker service: ACTIVE"
    else
        log_error "Celery worker service: FAILED"
        sudo systemctl status cyberctf-celery --no-pager
    fi
    
    if sudo systemctl is-active cyberctf-celerybeat >/dev/null; then
        log_info "Celery beat service: ACTIVE"
    else
        log_error "Celery beat service: FAILED"
        sudo systemctl status cyberctf-celerybeat --no-pager
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    sleep 5
    
    local health_checks_passed=0
    local total_checks=3
    
    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "✓ Backend health check: PASSED"
        ((health_checks_passed++))
    else
        log_error "✗ Backend health check: FAILED"
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
from app.core.database import SessionLocal
db = SessionLocal()
db.execute('SELECT 1')
db.close()
print('Database connection: OK')
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

# Main execution
main() {
    log_info "Starting backend-frontend integration..."
    
    detect_os
    log_info "Detected OS: $OS"
    
    check_user
    
    # Check if project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        log_info "Please deploy the project files first"
        exit 1
    fi
    
    setup_python_env
    setup_environment
    setup_database
    build_frontend
    setup_nginx
    create_services
    start_services
    health_check
    
    log_info "Backend-frontend integration completed!"
    log_info ""
    log_info "📋 Next steps:"
    log_info "   1. Access application at: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
    log_info "   2. Admin credentials: username=admin, password=admin123"
    log_info "   3. Check service status: sudo systemctl status cyberctf-backend"
    log_info "   4. View logs: sudo journalctl -u cyberctf-backend -f"
    log_info ""
    log_info "🔧 Management commands:"
    log_info "   Start: sudo systemctl start cyberctf-backend cyberctf-celery cyberctf-celerybeat"
    log_info "   Stop: sudo systemctl stop cyberctf-backend cyberctf-celery cyberctf-celerybeat"
    log_info "   Restart: sudo systemctl restart cyberctf-backend cyberctf-celery cyberctf-celerybeat"
    log_info ""
    log_info "⚠️  Important: Don't forget to:"
    log_info "   - Change default admin password"
    log_info "   - Configure email settings in $BACKEND_DIR/.env"
    log_info "   - Set up SSL certificate for production"
}

# Run main function
main "$@"
