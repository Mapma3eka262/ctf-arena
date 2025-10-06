#!/bin/bash

# Quick install script for CyberCTF Arena

set -e

echo "🚀 Starting CyberCTF Arena Quick Installation..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y git
    elif command -v yum &> /dev/null; then
        yum install -y git
    fi
fi

# Clone deploy scripts
echo "📥 Downloading deployment scripts..."
cd /tmp
if [ -d "cyberctf-arena" ]; then
    rm -rf cyberctf-arena
fi

git clone https://github.com/Mapma3eka262/cyberctf-arena.git
cd cyberctf-arena/deploy

# Make scripts executable
chmod +x *.sh

# Run setup
echo "🛠 Setting up server..."
./setup_server.sh

# Switch to cyberctf user and deploy
echo "📦 Deploying application..."
sudo -u cyberctf ./deploy_project.sh

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Quick start:"
echo "  Access: http://$(curl -s ifconfig.me)"
echo "  Admin: username=admin, password=admin123"
echo "  Manage: /home/cyberctf/cyberctf-arena/manage.sh"
echo ""
