#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Install Python 3.9 on CentOS 8
install_python39_centos() {
    log_info "Installing Python 3.9 on CentOS 8..."
    
    # Install EPEL and PowerTools
    dnf install -y epel-release
    dnf config-manager --set-enabled powertools
    
    # Install Python 3.9
    dnf install -y python39 python39-devel python39-pip
    
    # Create symlinks for python3 and pip3
    alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
    alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.9 1
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    log_info "Python 3.9 installed: $(python3 --version)"
    log_info "Pip installed: $(pip3 --version)"
}

# Install development tools
install_dev_tools() {
    log_info "Installing development tools..."
    
    if [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        # Для CentOS/RHEL
        dnf groupinstall -y "Development Tools"
        dnf install -y python3-devel postgresql-devel openssl-devel libffi-devel gcc-c++ make
    elif [ "$OS_ID" == "ubuntu" ]; then
        # Для Ubuntu
        apt-get install -y build-essential python3-dev libpq-dev libssl-dev libffi-dev
    else
        log_warn "Unknown OS, trying to install common development tools"
        dnf groupinstall -y "Development Tools" 2>/dev/null || \
        apt-get install -y build-essential 2>/dev/null || \
        log_error "Cannot install development tools"
    fi
}

# Install dependencies for Ubuntu
install_ubuntu() {
    log_info "Installing dependencies for Ubuntu..."
    
    # Update package list
    apt-get update
    
    # Install system dependencies
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        docker.io \
        docker-compose \
        git \
        curl \
        wget
    
    # Start and enable services
    systemctl start postgresql
    systemctl enable postgresql
    systemctl start redis-server
    systemctl enable redis-server
    systemctl start docker
    systemctl enable docker
}

# Install dependencies for CentOS
install_centos() {
    log_info "Installing dependencies for CentOS..."
    
    # Update package list
    dnf update -y
    
    # Install EPEL repository
    dnf install -y epel-release
    
    # Enable PowerTools repository for development packages
    dnf config-manager --set-enabled powertools
    
    # Install Python 3.9 first
    install_python39_centos
    
    # Install system dependencies
    dnf install -y \
        postgresql \
        postgresql-server \
        postgresql-contrib \
        redis \
        nginx \
        docker \
        git \
        curl \
        wget \
        policycoreutils-python-utils
    
    # Install docker-compose using pip3
    pip3 install docker-compose
    
    # Initialize and start PostgreSQL
    log_info "Initializing PostgreSQL..."
    postgresql-setup --initdb
    
    # Configure PostgreSQL to accept connections
    if [ -f "/var/lib/pgsql/data/pg_hba.conf" ]; then
        sed -i 's/^host.*ident$/host    all             all             127.0.0.1\/32            md5/' /var/lib/pgsql/data/pg_hba.conf
        sed -i 's/^host.*ident$/host    all             all             ::1\/128                 md5/' /var/lib/pgsql/data/pg_hba.conf
    fi
    
    # Start and enable services with correct service names
    systemctl start postgresql
    systemctl enable postgresql
    systemctl start redis
    systemctl enable redis
    systemctl start docker
    systemctl enable docker
    systemctl start nginx
    systemctl enable nginx
    
    # Configure SELinux for PostgreSQL if enabled
    if command -v getenforce >/dev/null 2>&1 && [ "$(getenforce)" == "Enforcing" ]; then
        setsebool -P httpd_can_network_connect 1
    fi
}

# Configure PostgreSQL
setup_postgresql() {
    log_info "Setting up PostgreSQL..."
    
    if [ "$OS_ID" == "ubuntu" ]; then
        sudo -u postgres psql -c "CREATE USER cyberctf WITH PASSWORD 'cyberctf2024';" || {
            log_error "Failed to create PostgreSQL user"
            return 1
        }
        sudo -u postgres psql -c "CREATE DATABASE cyberctf OWNER cyberctf;" || {
            log_error "Failed to create PostgreSQL database"
            return 1
        }
        sudo -u postgres psql -c "ALTER USER cyberctf CREATEDB;" || {
            log_error "Failed to grant privileges"
            return 1
        }
    elif [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        # For CentOS, we need to switch to postgres user
        sudo -i -u postgres psql -c "CREATE USER cyberctf WITH PASSWORD 'cyberctf2024';" || {
            log_error "Failed to create PostgreSQL user"
            return 1
        }
        sudo -i -u postgres psql -c "CREATE DATABASE cyberctf OWNER cyberctf;" || {
            log_error "Failed to create PostgreSQL database"
            return 1
        }
        sudo -i -u postgres psql -c "ALTER USER cyberctf CREATEDB;" || {
            log_error "Failed to grant privileges"
            return 1
        }
        
        # Restart PostgreSQL to apply changes
        systemctl restart postgresql
    fi
    
    log_info "PostgreSQL setup completed"
}

# Configure firewall
setup_firewall() {
    log_info "Configuring firewall..."
    
    if command -v ufw >/dev/null 2>&1; then
        # Ubuntu with ufw
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 8000/tcp
        ufw --force enable
        log_info "UFW firewall configured"
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS with firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --reload
        log_info "Firewalld configured"
    else
        log_warn "No firewall manager found, please configure firewall manually"
    fi
}

# Create application user
create_app_user() {
    log_info "Creating application user..."
    
    if ! id "cyberctf" &>/dev/null; then
        useradd -m -s /bin/bash cyberctf
        # Add to docker group if docker is installed
        if getent group docker >/dev/null; then
            usermod -aG docker cyberctf
        fi
        log_info "User 'cyberctf' created"
    else
        log_warn "User 'cyberctf' already exists"
    fi
}

# Install Python dependencies compatible with CentOS 8
install_python_deps_centos() {
    log_info "Installing Python dependencies for CentOS 8..."
    
    # Use python3 -m pip to avoid wrapper issues
    python3 -m pip install --upgrade pip
    
    # Install compatible versions for CentOS 8
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
    
    log_info "Python dependencies installed for CentOS 8"
}

# Install Python dependencies for Ubuntu
install_python_deps_ubuntu() {
    log_info "Installing Python dependencies for Ubuntu..."
    
    pip3 install --upgrade pip
    
    pip3 install \
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
    
    log_info "Python dependencies installed for Ubuntu"
}

# Install Python dependencies based on OS
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    if [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        install_python_deps_centos
    elif [ "$OS_ID" == "ubuntu" ]; then
        install_python_deps_ubuntu
    else
        log_warn "Unknown OS, trying Ubuntu-compatible dependencies"
        install_python_deps_ubuntu
    fi
}

# Check service status
check_services() {
    log_info "Checking service status..."
    
    local services=()
    
    if [ "$OS_ID" == "ubuntu" ]; then
        services=("postgresql" "redis-server" "docker" "nginx")
    elif [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        services=("postgresql" "redis" "docker" "nginx")
    fi
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service; then
            log_info "✓ $service: RUNNING"
        else
            log_error "✗ $service: NOT RUNNING"
        fi
    done
}

# Verify Python installation
verify_python() {
    log_info "Verifying Python installation..."
    
    log_info "Python version: $(python3 --version)"
    log_info "Pip version: $(python3 -m pip --version)"
    
    # Test key imports
    if python3 -c "import sqlalchemy; print('✓ SQLAlchemy OK')"; then
        log_info "✓ SQLAlchemy: OK"
    else
        log_error "✗ SQLAlchemy: FAILED"
    fi
    
    if python3 -c "import fastapi; print('✓ FastAPI OK')"; then
        log_info "✓ FastAPI: OK"
    else
        log_error "✗ FastAPI: FAILED"
    fi
    
    if python3 -c "import redis; print('✓ Redis OK')"; then
        log_info "✓ Redis: OK"
    else
        log_error "✗ Redis: FAILED"
    fi
    
    if python3 -c "import psycopg2; print('✓ Psycopg2 OK')"; then
        log_info "✓ Psycopg2: OK"
    else
        log_error "✗ Psycopg2: FAILED"
    fi
}

# Main execution
main() {
    log_info "Starting server setup..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root"
        exit 1
    fi
    
    detect_os
    log_info "Detected OS: $OS $OS_VERSION"
    
    # Install development tools first
    install_dev_tools
    
    # Install dependencies based on OS
    case $OS_ID in
        "ubuntu")
            install_ubuntu
            ;;
        "centos"|"rhel")
            install_centos
            ;;
        *)
            log_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    setup_postgresql
    setup_firewall
    create_app_user
    
    # Install Python dependencies
    install_python_deps
    
    # Verify installation
    verify_python
    
    # Check service status
    check_services
    
    log_info "Server setup completed successfully!"
    log_info ""
    log_info "📋 Next steps:"
    log_info "1. Deploy application code to /home/cyberctf/cyberctf-arena"
    log_info "2. Run integration script: sudo -u cyberctf ./deploy/integrate_frontend_backend.sh"
    log_info ""
    log_info "🔧 Service information:"
    log_info "   PostgreSQL: database=cyberctf, user=cyberctf, password=cyberctf2024"
    log_info "   Redis: running on localhost:6379"
    log_info "   Docker: installed and running"
    log_info "   Nginx: installed and running"
    log_info ""
    log_info "🐍 Python information:"
    log_info "   Version: $(python3 --version)"
    log_info "   Pip: $(python3 -m pip --version | cut -d' ' -f1-2)"
}

# Run main function
main "$@"
