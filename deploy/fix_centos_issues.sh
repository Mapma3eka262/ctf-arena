#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

fix_centos_services() {
    log_info "Fixing CentOS services..."
    
    # Check if we're on CentOS
    if [ ! -f /etc/centos-release ] && [ ! -f /etc/redhat-release ]; then
        log_error "This script is for CentOS/RHEL only"
        exit 1
    fi
    
    # Install missing packages
    dnf install -y postgresql postgresql-server postgresql-contrib redis nginx docker
    
    # Initialize PostgreSQL if not initialized
    if [ ! -d "/var/lib/pgsql/data" ]; then
        log_info "Initializing PostgreSQL..."
        postgresql-setup --initdb
    fi
    
    # Fix PostgreSQL authentication
    if [ -f "/var/lib/pgsql/data/pg_hba.conf" ]; then
        log_info "Configuring PostgreSQL authentication..."
        sed -i 's/^host.*ident$/host    all             all             127.0.0.1\/32            md5/' /var/lib/pgsql/data/pg_hba.conf
        sed -i 's/^host.*ident$/host    all             all             ::1\/128                 md5/' /var/lib/pgsql/data/pg_hba.conf
    fi
    
    # Start and enable services
    log_info "Starting services..."
    systemctl enable postgresql
    systemctl start postgresql
    
    systemctl enable redis
    systemctl start redis
    
    systemctl enable docker
    systemctl start docker
    
    systemctl enable nginx
    systemctl start nginx
    
    # Create cyberctf user in PostgreSQL
    log_info "Creating database user..."
    sudo -i -u postgres psql -c "CREATE USER cyberctf WITH PASSWORD 'cyberctf2024';" 2>/dev/null || log_warn "User may already exist"
    sudo -i -u postgres psql -c "CREATE DATABASE cyberctf OWNER cyberctf;" 2>/dev/null || log_warn "Database may already exist"
    sudo -i -u postgres psql -c "ALTER USER cyberctf CREATEDB;" 2>/dev/null || log_warn "Privileges may already be granted"
    
    log_info "CentOS services fixed"
}

install_dev_tools_centos() {
    log_info "Installing development tools for CentOS..."
    
    dnf groupinstall -y "Development Tools"
    dnf install -y python3-devel postgresql-devel openssl-devel libffi-devel gcc-c++
    
    log_info "Development tools installed"
}

main() {
    log_info "Fixing CentOS-specific issues..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root"
        exit 1
    fi
    
    install_dev_tools_centos
    fix_centos_services
    
    log_info "CentOS issues fixed successfully!"
}

main "$@"
