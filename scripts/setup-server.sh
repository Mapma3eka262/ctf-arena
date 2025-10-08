#!/bin/bash

set -e

echo "CTF Platform Server Setup Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_USER="ctf"
PROJECT_DIR="/opt/ctf-platform"
DOMAIN="ctf.example.com"
EMAIL="admin@${DOMAIN}"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root"
fi

# Update system
log "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
log "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    tree \
    unzip \
    zip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv

# Create project user
if ! id "$PROJECT_USER" &>/dev/null; then
    log "Creating project user: $PROJECT_USER"
    useradd -m -s /bin/bash -d "$PROJECT_DIR" "$PROJECT_USER"
    usermod -aG sudo "$PROJECT_USER"
else
    log "Project user $PROJECT_USER already exists"
fi

# Create directory structure
log "Creating directory structure..."
mkdir -p "$PROJECT_DIR"/{backend,frontend,nginx,ssl,backups,logs,uploads}
mkdir -p "$PROJECT_DIR/backend"/{app,alembic,static}
mkdir -p "$PROJECT_DIR/frontend"/{src,dist}

# Set permissions
chown -R "$PROJECT_USER":"$PROJECT_USER" "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR"

# Install and configure PostgreSQL 15+
log "Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

# Configure PostgreSQL
log "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE USER ctf_user WITH PASSWORD 'ctf_password';"
sudo -u postgres psql -c "CREATE DATABASE ctf_platform OWNER ctf_user;"
sudo -u postgres psql -c "ALTER USER ctf_user CREATEDB;"

# Update PostgreSQL configuration for better performance
PG_CONF="/etc/postgresql/15/main/postgresql.conf"
if [ -f "$PG_CONF" ]; then
    sed -i 's/#listen_addresses = '\''localhost'\''/listen_addresses = '\''localhost'\''/' "$PG_CONF"
    sed -i 's/#shared_buffers = 128MB/shared_buffers = 256MB/' "$PG_CONF"
    sed -i 's/#work_mem = 4MB/work_mem = 16MB/' "$PG_CONF"
    
    # Restart PostgreSQL
    systemctl restart postgresql
fi

# Install and configure Redis
log "Installing Redis..."
apt install -y redis-server

# Configure Redis
REDIS_CONF="/etc/redis/redis.conf"
if [ -f "$REDIS_CONF" ]; then
    sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' "$REDIS_CONF"
    sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' "$REDIS_CONF"
    sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' "$REDIS_CONF"
    
    # Restart Redis
    systemctl restart redis-server
fi

# Install Node.js 18+ (LTS)
log "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Verify Node.js installation
node --version
npm --version

# Install Nginx
log "Installing Nginx..."
apt install -y nginx

# Configure firewall
log "Configuring firewall..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Install Certbot for SSL
log "Installing Certbot..."
apt install -y certbot python3-certbot-nginx

# Setup Python environment
log "Setting up Python environment..."
sudo -u "$PROJECT_USER" python3 -m venv "$PROJECT_DIR/venv"

# Clone or setup project (replace with your git repository)
log "Setting up project files..."
cd "$PROJECT_DIR"

# If you have a git repository, use this:
# sudo -u "$PROJECT_USER" git clone https://github.com/your-username/ctf-platform.git .

# Otherwise, we'll create the basic structure
cat > "$PROJECT_DIR/backend/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
celery==5.3.4
python-multipart==0.0.6
email-validator==2.1.0
python-dateutil==2.8.2
aiofiles==23.2.1
httpx==0.25.2
pillow==10.1.0
EOF

# Install Python dependencies
log "Installing Python dependencies..."
sudo -u "$PROJECT_USER" "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/backend/requirements.txt"

# Setup frontend dependencies
cat > "$PROJECT_DIR/frontend/package.json" << 'EOF'
{
  "name": "ctf-platform-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "alpinejs": "^3.13.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "vite": "^5.0.0"
  }
}
EOF

# Install frontend dependencies
log "Installing frontend dependencies..."
cd "$PROJECT_DIR/frontend"
sudo -u "$PROJECT_USER" npm install --no-audit --fund=false

# Игнорируем npm предупреждения и уязвимости для production
log "Frontend dependencies installed (warnings ignored for production)"

# Create basic frontend structure
sudo -u "$PROJECT_USER" mkdir -p "$PROJECT_DIR/frontend/src"/{components,pages,styles}

# Create Nginx configuration
# Create Nginx configuration with fallback for missing SSL
log "Configuring Nginx..."
cat > "$PROJECT_DIR/nginx/ctf-platform.conf" << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Frontend
    location / {
        root $PROJECT_DIR/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
    
    # API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Static files
    location /static {
        alias $PROJECT_DIR/backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # File uploads
    location /uploads {
        alias $PROJECT_DIR/uploads;
        internal;
    }
    
    # Security
    location ~ /\. {
        deny all;
    }
    
    location ~ /(README|LICENSE|CHANGELOG) {
        deny all;
    }
}
EOF

# Enable Nginx site
ln -sf "$PROJECT_DIR/nginx/ctf-platform.conf" /etc/nginx/sites-available/ctf-platform
ln -sf /etc/nginx/sites-available/ctf-platform /etc/nginx/sites-enabled/

# Remove default Nginx site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Create systemd service files
log "Creating systemd services..."

# Backend API service
cat > /etc/systemd/system/ctf-api.service << EOF
[Unit]
Description=CTF Platform API
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
cat > /etc/systemd/system/ctf-celery.service << EOF
[Unit]
Description=CTF Platform Celery Worker
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/venv/bin/celery -A app.workers.tasks.celery_app worker --loglevel=info --concurrency=4
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Celery beat service
cat > /etc/systemd/system/ctf-celery-beat.service << EOF
[Unit]
Description=CTF Platform Celery Beat
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/venv/bin/celery -A app.workers.tasks.celery_app beat --loglevel=info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Create backup script
log "Creating backup script..."
cat > "$PROJECT_DIR/scripts/backup.sh" << 'EOF'
#!/bin/bash

set -e

# Configuration
PROJECT_DIR="/opt/ctf-platform"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting backup..."

# Backup PostgreSQL database
log "Backing up database..."
sudo -u postgres pg_dump ctf_platform > "$BACKUP_DIR/database_$DATE.sql"

# Backup uploads and important directories
log "Backing up files..."
tar -czf "$BACKUP_FILE" \
    "$PROJECT_DIR/uploads" \
    "$PROJECT_DIR/backend/app" \
    "$PROJECT_DIR/nginx" \
    "$BACKUP_DIR/database_$DATE.sql"

# Remove temporary database dump
rm "$BACKUP_DIR/database_$DATE.sql"

# Keep only last 7 backups
log "Cleaning up old backups..."
ls -t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +8 | xargs -r rm

log "Backup completed: $BACKUP_FILE"

# Optional: Upload to remote storage
# echo "Uploading to remote storage..."
# rclone copy "$BACKUP_FILE" remote:ctf-backups/
EOF

chmod +x "$PROJECT_DIR/scripts/backup.sh"

# Create log rotation configuration
log "Configuring log rotation..."
cat > /etc/logrotate.d/ctf-platform << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Set proper permissions
log "Setting permissions..."
chown -R "$PROJECT_USER":"$PROJECT_USER" "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR/scripts/"*.sh

# Create initial environment configuration
log "Creating environment configuration..."
sudo -u "$PROJECT_USER" cat > "$PROJECT_DIR/backend/.env" << EOF
# CTF Platform Configuration
PROJECT_NAME=CTF Platform
VERSION=1.0.0

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=ctf_user
POSTGRES_PASSWORD=ctf_password
POSTGRES_DB=ctf_platform
DATABASE_URL=postgresql://ctf_user:ctf_password@localhost:5432/ctf_platform

# Redis
REDIS_URL=redis://localhost:6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=$PROJECT_DIR/uploads
MAX_FILE_SIZE=10485760
EOF

# Test Nginx configuration with HTTP only first
nginx -t
systemctl start nginx

# Generate SSL certificate only if domain resolves correctly
if [ "$DOMAIN" != "ctf.example.com" ]; then
    log "Testing domain resolution for $DOMAIN..."
    
    # Check if domain resolves to this server's IP
    DOMAIN_IP=$(dig +short "$DOMAIN" | head -1)
    SERVER_IP=$(curl -s http://ipinfo.io/ip || hostname -I | awk '{print $1}')
    
    if [ -n "$DOMAIN_IP" ] && [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
        log "Domain $DOMAIN correctly points to this server ($SERVER_IP)"
        log "Generating SSL certificate for $DOMAIN..."
        
        if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect; then
            log "SSL certificate successfully generated"
        else
            warn "SSL certificate generation failed. Continuing with HTTP only."
            warn "You can generate SSL later with: certbot --nginx -d $DOMAIN"
        fi
    else
        warn "Domain $DOMAIN does not resolve to this server."
        warn "Current DNS: $DOMAIN -> $DOMAIN_IP"
        warn "Server IP: $SERVER_IP"
        warn "Please configure DNS A record for $DOMAIN to point to $SERVER_IP"
        warn "SSL certificate generation skipped. You can add it later."
    fi
else
    warn "Default domain detected. Please set real DOMAIN in script configuration."
    warn "SSL certificate generation skipped."
fi

# Ensure Nginx is running with current config
systemctl reload nginx

# Start and enable services
log "Starting services..."
systemctl daemon-reload
systemctl enable postgresql redis-server nginx
systemctl start postgresql redis-server nginx

systemctl enable ctf-api ctf-celery ctf-celery-beat
systemctl start ctf-api ctf-celery ctf-celery-beat

# Create initial database tables (if backend code is available)
log "Setting up initial database..."
if [ -f "$PROJECT_DIR/backend/app/main.py" ]; then
    sudo -u "$PROJECT_USER" "$PROJECT_DIR/venv/bin/python" -c "
import sys
sys.path.append('$PROJECT_DIR/backend')
from app.core.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
else
    warn "Backend code not found. Please deploy your application code to $PROJECT_DIR/backend"
fi

# Print completion message
log "Server setup completed successfully!"
echo ""
info "Project Directory: $PROJECT_DIR"
info "Project User: $PROJECT_USER"
info "Domain: $DOMAIN"
info "Database: ctf_platform (user: ctf_user)"
info "Redis: Running on localhost:6379"
echo ""
info "Services:"
systemctl status ctf-api --no-pager
echo ""
systemctl status ctf-celery --no-pager
echo ""
systemctl status ctf-celery-beat --no-pager
echo ""
info "Next steps:"
echo "1. Deploy your application code to $PROJECT_DIR/backend"
echo "2. Build frontend: cd $PROJECT_DIR/frontend && npm run build"
echo "3. Configure your domain DNS to point to this server"
echo "4. Update the .env file with your actual configuration"
echo "5. Restart services: systemctl restart ctf-api ctf-celery ctf-celery-beat nginx"
echo ""
info "Backup script: $PROJECT_DIR/scripts/backup.sh"
info "Logs: journalctl -u ctf-api -f"
