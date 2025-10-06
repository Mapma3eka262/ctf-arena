#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/cyberctf/cyberctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found. Installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        else
            log_error "Cannot install Python3 automatically"
            exit 1
        fi
    fi
    
    log_info "Python version: $(python3 --version)"
}

recreate_venv() {
    log_info "Recreating virtual environment..."
    
    cd $BACKEND_DIR
    
    # Удаляем старую виртуальную среду
    if [ -d "$VENV_DIR" ]; then
        log_info "Removing existing virtual environment..."
        rm -rf $VENV_DIR
    fi
    
    # Создаем новую виртуальную среду
    log_info "Creating new virtual environment..."
    python3 -m venv $VENV_DIR
    
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi
    
    log_info "Virtual environment created at: $VENV_DIR"
}

install_dependencies() {
    log_info "Installing dependencies..."
    
    cd $BACKEND_DIR
    source $VENV_DIR/bin/activate
    
    # Обновляем pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Устанавливаем зависимости по одной для лучшего контроля
    log_info "Installing core dependencies..."
    
    # Основные зависимости
    pip install fastapi==0.104.1
    pip install uvicorn==0.24.0
    pip install sqlalchemy==2.0.23
    pip install psycopg2-binary==2.9.9
    pip install alembic==1.12.1
    pip install python-jose[cryptography]==3.3.0
    pip install passlib[bcrypt]==1.7.4
    pip install python-multipart==0.0.6
    pip install redis==5.0.1
    pip install celery==5.3.4
    pip install python-telegram-bot==20.7
    pip install pydantic==2.5.0
    pip install pydantic-settings==2.1.0
    pip install email-validator==2.1.0
    pip install python-i18n==0.3.9
    pip install httpx==0.25.2
    pip install aiofiles==23.2.1
    pip install python-dateutil==2.8.2
    
    log_info "All dependencies installed"
}

verify_installation() {
    log_info "Verifying installation..."
    
    cd $BACKEND_DIR
    source $VENV_DIR/bin/activate
    
    local checks=(
        "sqlalchemy"
        "fastapi" 
        "pydantic"
        "alembic"
        "celery"
        "redis"
        "psycopg2"
    )
    
    local passed=0
    local total=${#checks[@]}
    
    for package in "${checks[@]}"; do
        if python -c "import $package; print('✓ $package')" 2>/dev/null; then
            log_info "✓ $package: OK"
            ((passed++))
        else
            log_error "✗ $package: FAILED"
        fi
    done
    
    if [ $passed -eq $total ]; then
        log_info "🎉 All packages installed successfully!"
        return 0
    else
        log_error "Only $passed out of $total packages installed correctly"
        return 1
    fi
}

test_database_connection() {
    log_info "Testing database connection..."
    
    cd $BACKEND_DIR
    source $VENV_DIR/bin/activate
    
    if python -c "
import sys
sys.path.append('$BACKEND_DIR')
from app.core.database import engine, SessionLocal
print('✓ Database engine created successfully')
db = SessionLocal()
db.execute('SELECT 1')
db.close()
print('✓ Database connection test passed')
"; then
        log_info "✓ Database connection: OK"
        return 0
    else
        log_error "✗ Database connection: FAILED"
        return 1
    fi
}

main() {
    log_info "Starting dependency reinstallation..."
    
    if [ "$(whoami)" != "cyberctf" ]; then
        log_error "This script must be run as 'cyberctf' user"
        log_info "Run: sudo -u cyberctf $0"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi
    
    check_python
    recreate_venv
    install_dependencies
    verify_installation
    test_database_connection
    
    log_info "Dependency reinstallation completed!"
    log_info "You can now run the integration script again."
}

main "$@"
