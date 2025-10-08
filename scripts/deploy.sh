#!/bin/bash

set -e

echo "Deploying CTF Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/opt/ctf-platform"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$PROJECT_DIR/venv"

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root"
fi

# Backup database
log "Backing up database..."
sudo -u postgres pg_dump ctf_platform > $PROJECT_DIR/backups/ctf_platform_$(date +%Y%m%d_%H%M%S).sql

# Stop services
log "Stopping services..."
systemctl stop ctf-api ctf-celery ctf-celery-beat

# Update backend
log "Updating backend..."
cd $BACKEND_DIR
git pull origin main

# Update Python dependencies
log "Updating Python dependencies..."
source $VENV_DIR/bin/activate
pip install -r requirements.txt

# Run database migrations
log "Running database migrations..."
alembic upgrade head

# Build frontend
log "Building frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Start services
log "Starting services..."
systemctl start ctf-api ctf-celery ctf-celery-beat

log "Deployment completed successfully!"