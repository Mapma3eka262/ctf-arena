#!/bin/bash

set -e

echo "CTF Platform Monitoring Setup"
echo "============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/opt/ctf-platform"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Install monitoring tools
log "Installing monitoring tools..."
apt update
apt install -y \
    htop \
    iotop \
    nethogs \
    nmon \
    dstat \
    sysstat

# Enable sysstat
sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
systemctl enable sysstat
systemctl start sysstat

# Install and configure fail2ban
log "Installing fail2ban..."
apt install -y fail2ban

# Configure fail2ban for CTF platform
cat > /etc/fail2ban/jail.d/ctf-platform.conf << EOF
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[ctf-auth]
enabled = true
port = http,https
logpath = $PROJECT_DIR/logs/auth.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Create log monitoring script
cat > "$PROJECT_DIR/scripts/monitor-logs.sh" << 'EOF'
#!/bin/bash

# Monitor CTF platform logs for issues

LOG_FILE="$PROJECT_DIR/logs/application.log"
ERROR_PATTERNS=(
    "ERROR"
    "Exception"
    "Traceback"
    "500 Internal Server Error"
)

echo "Monitoring CTF platform logs..."
tail -F "$LOG_FILE" | while read line; do
    for pattern in "${ERROR_PATTERNS[@]}"; do
        if echo "$line" | grep -q "$pattern"; then
            echo "[ALERT] Found error in logs: $line"
            # Add notification logic here (email, telegram, etc.)
        fi
    done
done
EOF

chmod +x "$PROJECT_DIR/scripts/monitor-logs.sh"

# Create health check script
cat > "$PROJECT_DIR/scripts/health-check.sh" << 'EOF'
#!/bin/bash

# Health check for CTF platform services

SERVICES=("ctf-api" "ctf-celery" "ctf-celery-beat" "nginx" "postgresql" "redis-server")
ALERT=false
MESSAGE=""

for service in "${SERVICES[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        ALERT=true
        MESSAGE="$MESSAGE\n❌ Service $service is not running"
    else
        echo "✅ Service $service is running"
    fi
done

# Check disk space
DISK_USAGE=$(df / --output=pcent | tail -1 | tr -d ' %')
if [ "$DISK_USAGE" -gt 80 ]; then
    ALERT=true
    MESSAGE="$MESSAGE\n❌ Disk usage is high: ${DISK_USAGE}%"
fi

# Check memory
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -gt 80 ]; then
    ALERT=true
    MESSAGE="$MESSAGE\n❌ Memory usage is high: ${MEM_USAGE}%"
fi

if [ "$ALERT" = true ]; then
    echo -e "CTF Platform Health Check Alert:$MESSAGE"
    # Add notification logic here
else
    echo "✅ All systems operational"
fi
EOF

chmod +x "$PROJECT_DIR/scripts/health-check.sh"

# Add cron jobs for monitoring
log "Setting up monitoring cron jobs..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/scripts/health-check.sh > /dev/null 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/scripts/backup.sh > /dev/null 2>&1") | crontab -

log "Monitoring setup completed!"
echo ""
echo "Installed tools:"
echo "✅ htop, iotop, nethogs - system monitoring"
echo "✅ sysstat - system statistics"
echo "✅ fail2ban - security monitoring"
echo "✅ Custom health check scripts"
echo "✅ Cron jobs for automated monitoring"