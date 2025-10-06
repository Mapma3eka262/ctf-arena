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
        VER=$VERSION_ID
    else
        log_error "Cannot detect OS"
        exit 1
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
    yum update -y
    
    # Install EPEL repository
    yum install -y epel-release
    
    # Install system dependencies
    yum install -y \
        python3 \
        python3-pip
        
    pip3 install --upgrade pip

    yum install -y \
        postgresql \
        postgresql-server \
        postgresql-contrib \
        redis \
        nginx \
        docker \
        git \
        curl \
        wget
    
    # Install docker-compose separately
    pip3 install docker-compose
    pip3 install SQLAlchemy
    
    # Initialize and start services
    postgresql-setup initdb
    systemctl start postgresql
    systemctl enable postgresql
    systemctl start redis
    systemctl enable redis
    systemctl start docker
    systemctl enable docker
    systemctl start nginx
    systemctl enable nginx
}

# Configure PostgreSQL
setup_postgresql() {
    log_info "Setting up PostgreSQL..."
    
    if [ "$OS" == "Ubuntu" ]; then
        sudo -u postgres psql -c "CREATE USER cyberctf WITH PASSWORD 'cyberctf2024';"
        sudo -u postgres psql -c "CREATE DATABASE cyberctf OWNER cyberctf;"
        sudo -u postgres psql -c "ALTER USER cyberctf CREATEDB;"
    elif [ "$OS" == "CentOS Linux" ]; then
        sudo -u postgres psql -c "CREATE USER cyberctf WITH PASSWORD 'cyberctf2024';"
        sudo -u postgres psql -c "CREATE DATABASE cyberctf OWNER cyberctf;"
        sudo -u postgres psql -c "ALTER USER cyberctf CREATEDB;"
        
        # Configure PostgreSQL authentication
        sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' /var/lib/pgsql/data/pg_hba.conf
        systemctl restart postgresql
    fi
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
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS with firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --reload
    fi
}

# Create application user
create_app_user() {
    log_info "Creating application user..."
    
    if ! id "cyberctf" &>/dev/null; then
        useradd -m -s /bin/bash cyberctf
        usermod -aG docker cyberctf
        log_info "User 'cyberctf' created"
    else
        log_warn "User 'cyberctf' already exists"
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
    log_info "Detected OS: $OS"
    
    # Install dependencies based on OS
    case $OS in
        "Ubuntu")
            install_ubuntu
            ;;
        "CentOS Linux")
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
    
    log_info "Server setup completed successfully!"
    log_info "Next steps:"
    log_info "1. Deploy application code to /home/cyberctf/cyberctf-arena"
    log_info "2. Run integration script"
}

# Run main function
main "$@"
