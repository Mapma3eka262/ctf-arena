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

# Configure Russian repositories
configure_russian_repos() {
    log_info "Configuring Russian repositories..."
    
    # Backup original repos
    mkdir -p /etc/yum.repos.d/backup
    cp /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/
    
    # For AlmaLinux/Rocky Linux - use Russian mirrors
    if [ -f /etc/alma-release ] || [ -f /etc/rocky-release ]; then
        log_info "Configuring Russian mirrors for AlmaLinux/RockyLinux..."
        
        # AlmaLinux Russian mirrors
        cat > /etc/yum.repos.d/alma-russian.repo << 'EOF'
[baseos-ru]
name=AlmaLinux $releasever - BaseOS Russian Mirrors
baseurl=http://mirrors.rosalinux.ru/almalinux/$releasever/BaseOS/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux

[appstream-ru]
name=AlmaLinux $releasever - AppStream Russian Mirrors  
baseurl=http://mirrors.rosalinux.ru/almalinux/$releasever/AppStream/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux

[extras-ru]
name=AlmaLinux $releasever - Extras Russian Mirrors
baseurl=http://mirrors.rosalinux.ru/almalinux/$releasever/extras/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux

[epel-ru]
name=EPEL Russian Mirrors
baseurl=http://mirrors.rosalinux.ru/epel/$releasever/Everything/$basearch/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-8
EOF
    fi
    
    # For CentOS 8 - use vault.centos.org
    if [ -f /etc/centos-release ]; then
        log_info "Configuring CentOS 8 vault repositories..."
        
        # Disable original repos
        sed -i 's/enabled=1/enabled=0/g' /etc/yum.repos.d/CentOS-*
        
        # Add vault repositories
        cat > /etc/yum.repos.d/CentOS-Vault.repo << 'EOF'
[C8-baseos-vault]
name=CentOS-8 - BaseOS Vault
baseurl=http://vault.centos.org/8.5.2111/BaseOS/$basearch/os/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
enabled=1

[C8-appstream-vault]
name=CentOS-8 - AppStream Vault  
baseurl=http://vault.centos.org/8.5.2111/AppStream/$basearch/os/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
enabled=1

[C8-extras-vault]
name=CentOS-8 - Extras Vault
baseurl=http://vault.centos.org/8.5.2111/extras/$basearch/os/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
enabled=1

[C8-epel-vault]
name=EPEL 8 Vault
baseurl=https://archives.fedoraproject.org/pub/archive/epel/8/Everything/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-8
enabled=1
EOF
    fi
    
    # Clean cache
    dnf clean all
    dnf makecache
    
    log_info "Russian repositories configured"
}

# Configure Russian locale and timezone
configure_localization() {
    log_info "Configuring Russian localization..."
    
    # Set timezone to Moscow
    timedatectl set-timezone Europe/Moscow
    
    # Install Russian locale
    dnf install -y glibc-langpack-ru
    
    # Generate Russian locale
    localedef -c -i ru_RU -f UTF-8 ru_RU.UTF-8
    
    # Set system language
    localectl set-locale LANG=ru_RU.UTF-8
    
    log_info "Localization configured: Timezone=$(timedatectl show --property=Timezone --value), Locale=ru_RU.UTF-8"
}

# Configure Russian NTP servers
configure_ntp() {
    log_info "Configuring Russian NTP servers..."
    
    # Install chrony
    dnf install -y chrony
    
    # Configure Russian NTP servers
    cat > /etc/chrony.conf << 'EOF'
# Russian NTP servers
server ntp1.stratum2.ru iburst
server ntp2.stratum2.ru iburst  
server ntp3.stratum2.ru iburst
server ntp1.vniiftri.ru iburst
server ntp2.vniiftri.ru iburst
server time.cloud.ru iburst

# Allow NTP client access from local network
allow 192.168.0.0/16
allow 10.0.0.0/8
allow 172.16.0.0/12

# Serve time even if not synchronized to any NTP server
local stratum 10

# Record the rate at which the system clock gains/losses time
driftfile /var/lib/chrony/drift

# Allow the system clock to be stepped in the first three updates
# if its offset is larger than 1 second
makestep 1.0 3

# Enable kernel synchronization of the real-time clock
rtcsync

# Enable hardware timestamping on all interfaces that support it
#hwtimestamp *

# Increase the minimum number of selectable sources required to adjust
# the system clock
minsources 2

# Allow NTP client access from local network
#allow 192.168.1.0/24

# Serve time even if not synchronized to a time source
local stratum 10

# Specify file containing keys for NTP authentication
keyfile /etc/chrony.keys

# Specify directory for log files
logdir /var/log/chrony

# Select which information is logged
log measurements statistics tracking
EOF
    
    systemctl enable chronyd
    systemctl restart chronyd
    
    log_info "NTP configured with Russian servers"
}

# Configure Russian DNS servers
configure_dns() {
    log_info "Configuring Russian DNS servers..."
    
    # Install resolv.conf management
    dnf install -y systemd-resolved
    
    # Configure Russian DNS servers
    cat > /etc/systemd/resolved.conf << 'EOF'
[Resolve]
DNS=77.88.8.8 77.88.8.1 1.1.1.1 8.8.8.8
FallbackDNS=77.88.8.88 77.88.8.2
Domains=~.
DNSSEC=allow-downgrade
DNSOverTLS=opportunistic
Cache=yes
DNSStubListener=yes
ReadEtcHosts=yes
EOF
    
    systemctl enable systemd-resolved
    systemctl restart systemd-resolved
    
    # Create symlink
    ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
    
    log_info "DNS configured with Russian servers (Yandex DNS)"
}

# Configure Russian Python PyPI mirrors
configure_python_mirrors() {
    log_info "Configuring Russian PyPI mirrors..."
    
    # Create pip configuration for Russian mirrors
    mkdir -p /etc/pip
    cat > /etc/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
extra-index-url = 
    https://pypi.douban.com/simple/
    https://mirrors.aliyun.com/pypi/simple/
    https://pypi.org/simple

trusted-host = 
    pypi.tuna.tsinghua.edu.cn
    pypi.douban.com
    mirrors.aliyun.com
    pypi.org
    files.pythonhosted.org

timeout = 120
retries = 5
EOF
    
    # For current user
    mkdir -p ~/.pip
    cp /etc/pip.conf ~/.pip/pip.conf
    
    log_info "PyPI mirrors configured with Chinese/Russian alternatives"
}

# Configure Russian Docker mirrors
configure_docker_mirrors() {
    log_info "Configuring Russian Docker mirrors..."
    
    # Create docker daemon configuration
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.rosalinux.ru",
    "https://registry.mirror.su/",
    "https://dockerhub.ir",
    "https://dockerproxy.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF
    
    log_info "Docker mirrors configured with Russian alternatives"
}

# Configure Russian Git mirrors
configure_git_mirrors() {
    log_info "Configuring Git for Russian servers..."
    
    # Configure git to use HTTPS and increase buffer
    git config --global http.sslVerify true
    git config --global http.postBuffer 1048576000
    git config --global core.compression 9
    
    # Add Russian GitHub mirrors to hosts file as backup
    echo "# GitHub mirrors for Russia" >> /etc/hosts
    echo "185.199.108.153 assets-cdn.github.com" >> /etc/hosts
    echo "185.199.109.153 assets-cdn.github.com" >> /etc/hosts
    echo "185.199.110.153 assets-cdn.github.com" >> /etc/hosts
    echo "185.199.111.153 assets-cdn.github.com" >> /etc/hosts
    
    log_info "Git configured for better performance in Russia"
}

# Configure system optimizations for Russian networks
configure_system_optimizations() {
    log_info "Configuring system optimizations for Russian networks..."
    
    # Increase TCP buffer sizes for better performance on high-latency links
    cat > /etc/sysctl.d/99-russian-network.conf << 'EOF'
# Russian network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 16384 16777216
net.ipv4.tcp_congestion_control = cubic
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15

# Increase connection limits
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Security settings
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
EOF
    
    # Apply settings
    sysctl -p /etc/sysctl.d/99-russian-network.conf
    
    # Configure firewalld for Russian standards
    if systemctl is-active firewalld >/dev/null 2>&1; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --reload
    fi
    
    log_info "System optimizations applied for Russian networks"
}

# Install Russian SSL certificates
install_russian_certificates() {
    log_info "Installing Russian SSL certificates..."
    
    # Update CA certificates
    dnf install -y ca-certificates
    
    # Download and install Russian root certificates
    curl -s https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer -o /etc/pki/ca-trust/source/anchors/russian_trusted_root_ca.crt
    curl -s https://gu-st.ru/content/Other/doc/russian_trusted_sub_ca.cer -o /etc/pki/ca-trust/source/anchors/russian_trusted_sub_ca.crt
    
    # Update CA trust
    update-ca-trust
    
    log_info "Russian SSL certificates installed"
}

# Main configuration function
main() {
    log_info "Starting Russian Federation server configuration..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root"
        exit 1
    fi
    
    # Detect OS
    if [ -f /etc/alma-release ]; then
        log_info "Detected AlmaLinux"
    elif [ -f /etc/rocky-release ]; then
        log_info "Detected Rocky Linux"
    elif [ -f /etc/centos-release ]; then
        log_info "Detected CentOS"
    else
        log_error "Unsupported OS. This script works with AlmaLinux, Rocky Linux, or CentOS 8"
        exit 1
    fi
    
    configure_russian_repos
    configure_localization
    configure_ntp
    configure_dns
    configure_python_mirrors
    configure_docker_mirrors
    configure_git_mirrors
    configure_system_optimizations
    install_russian_certificates
    
    log_info "🎉 Russian Federation server configuration completed!"
    log_info ""
    log_info "📋 Configuration summary:"
    log_info "   • Russian repositories configured"
    log_info "   • Timezone: Europe/Moscow"
    log_info "   • Locale: ru_RU.UTF-8" 
    log_info "   • Russian NTP servers"
    log_info "   • Russian DNS servers (Yandex)"
    log_info "   • Chinese/Russian PyPI mirrors"
    log_info "   • Russian Docker mirrors"
    log_info "   • Network optimizations for high latency"
    log_info "   • Russian SSL certificates"
    log_info ""
    log_info "🚀 Now you can run the CyberCTF Arena installation scripts."
}

main "$@"
