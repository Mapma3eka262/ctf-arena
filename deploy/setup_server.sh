#!/bin/bash

# CyberCTF Arena - Setup Script for Ubuntu 24.04
set -e

echo "🚀 Начало настройки сервера для CyberCTF Arena..."

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root: sudo ./setup_server.sh"
    exit 1
fi

# Обновление системы
echo "📦 Обновление пакетов системы..."
apt update && apt upgrade -y

# Установка базовых пакетов
echo "📦 Установка системных зависимостей..."
apt install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    supervisor \
    fail2ban \
    ufw \
    htop \
    net-tools

# Настройка брандмауэра
echo "🔥 Настройка брандмауэра..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000
ufw --force enable

# Настройка PostgreSQL
echo "🐘 Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE USER ctfuser WITH PASSWORD 'ctfpassword';"
sudo -u postgres psql -c "CREATE DATABASE ctfarena OWNER ctfuser;"
sudo -u postgres psql -c "ALTER USER ctfuser CREATEDB;"

# Настройка Redis
echo "🔴 Настройка Redis..."
systemctl enable redis-server
systemctl start redis-server

# Создание пользователя для приложения
echo "👤 Создание пользователя приложения..."
if ! id "ctf" &>/dev/null; then
    useradd -m -s /bin/bash ctf
    usermod -aG sudo ctf
fi

# Создание директорий
echo "📁 Создание структуры директорий..."
mkdir -p /opt/ctf-arena/{backend,frontend,logs,backups,uploads}
chown -R ctf:ctf /opt/ctf-arena

# Настройка прав
chmod 755 /opt/ctf-arena
chmod 755 /opt/ctf-arena/backups

echo "✅ Настройка сервера завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте SSL сертификат: certbot --nginx"
echo "2. Запустите скрипт интеграции: ./integrate_frontend_backend.sh"
echo "3. Запустите деплой: ./deploy_project.sh"