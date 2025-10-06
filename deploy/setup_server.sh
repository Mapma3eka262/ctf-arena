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

# Install development tools
install_dev_tools() {
    log_info "Installing development tools..."
    
    if [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        # Для CentOS/RHEL
        yum groupinstall -y "Development Tools"
        yum install -y python3-devel postgresql-devel openssl-devel libffi-devel
    elif [ "$OS_ID" == "ubuntu" ]; then
        # Для Ubuntu
        apt-get install -y build-essential python3-dev libpq-dev libssl-dev libffi-dev
    else
        log_warn "Unknown OS, trying to install common development tools"
        yum groupinstall -y "Development Tools" 2>/dev/null || \
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
    
    # Install system dependencies
    dnf install -y \
        python3 \
        python3-pip \
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
    
    # Install docker-compose
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

# Install Python dependencies without compilation issues
install_python_deps_safe() {
    log_info "Installing Python dependencies safely..."
    
    # Create a temporary directory for pip cache
    export PIP_CACHE_DIR=/tmp/pip_cache
    mkdir -p $PIP_CACHE_DIR
    
    # Set environment variables to avoid compilation
    export CRYPTOGRAPHY_DONT_BUILD_RUST=1
    
    # Install precompiled wheels where possible
    pip3 install --no-cache-dir --upgrade pip
    
    # Install dependencies that don't require compilation first
    pip3 install --no-cache-dir \
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
        python-telegram-bot==20.7
    
    # Try to install psycopg2-binary (precompiled)
    pip3 install --no-cache-dir psycopg2-binary==2.9.9 || {
        log_warn "psycopg2-binary failed, trying psycopg2"
        pip3 install --no-cache-dir psycopg2==2.9.9
    }
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
    
    # Install Python dependencies globally for system tools
    install_python_deps_safe
    
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
    log_info "⚠️  If any services failed to start, check:"
    log_info "   - systemctl status <service-name>"
    log_info "   - journalctl -u <service-name> -f"
}

# Run main function
main "$@"
