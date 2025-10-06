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

fix_database_py() {
    log_info "Fixing database.py imports..."
    
    cat > $BACKEND_DIR/app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создание движка базы данных
engine = create_engine(settings.DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Dependency для получения сессии базы данных.
    Используется в FastAPI dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
    
    log_info "database.py fixed"
}

reinstall_dependencies() {
    log_info "Reinstalling Python dependencies..."
    
    cd $BACKEND_DIR
    
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found at $VENV_DIR"
        return 1
    fi
    
    source $VENV_DIR/bin/activate
    
    # Удаляем и переустанавливаем зависимости
    pip freeze | xargs pip uninstall -y
    pip install --upgrade pip
    
    # Устанавливаем зависимости заново
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
    
    log_info "Dependencies reinstalled"
}

verify_installation() {
    log_info "Verifying installation..."
    
    cd $BACKEND_DIR
    source $VENV_DIR/bin/activate
    
    local checks_passed=0
    local total_checks=5
    
    # Проверка SQLAlchemy
    if python -c "import sqlalchemy; print('✓ SQLAlchemy')" 2>/dev/null; then
        log_info "✓ SQLAlchemy: OK"
        ((checks_passed++))
    else
        log_error "✗ SQLAlchemy: FAILED"
    fi
    
    # Проверка FastAPI
    if python -c "import fastapi; print('✓ FastAPI')" 2>/dev/null; then
        log_info "✓ FastAPI: OK"
        ((checks_passed++))
    else
        log_error "✗ FastAPI: FAILED"
    fi
    
    # Проверка Pydantic
    if python -c "import pydantic; print('✓ Pydantic')" 2>/dev/null; then
        log_info "✓ Pydantic: OK"
        ((checks_passed++))
    else
        log_error "✗ Pydantic: FAILED"
    fi
    
    # Проверка Alembic
    if python -c "import alembic; print('✓ Alembic')" 2>/dev/null; then
        log_info "✓ Alembic: OK"
        ((checks_passed++))
    else
        log_error "✗ Alembic: FAILED"
    fi
    
    # Проверка импорта database.py
    if python -c "from app.core.database import engine, SessionLocal; print('✓ Database imports')" 2>/dev/null; then
        log_info "✓ Database imports: OK"
        ((checks_passed++))
    else
        log_error "✗ Database imports: FAILED"
    fi
    
    if [ $checks_passed -eq $total_checks ]; then
        log_info "🎉 All dependency checks passed!"
        return 0
    else
        log_error "Only $checks_passed out of $total_checks checks passed"
        return 1
    fi
}

main() {
    log_info "Fixing dependencies and imports..."
    
    if [ "$(whoami)" != "cyberctf" ]; then
        log_error "This script must be run as 'cyberctf' user"
        log_info "Run: sudo -u cyberctf $0"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi
    
    fix_database_py
    reinstall_dependencies
    verify_installation
    
    log_info "Fix completed! Try running the application again."
}

main "$@"
