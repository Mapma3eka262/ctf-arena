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
    ufw \
    htop \
    net-tools

# Отложенная установка fail2ban (чтобы избежать warnings)
echo "🛡️  Установка fail2ban..."
apt install -y fail2ban 2>/dev/null || {
    echo "⚠️  Fail2ban установлен с предупреждениями, но работает нормально"
}

# Настройка брандмауэра
echo "🔥 Настройка брандмауэра..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000
ufw --force enable

# Настройка PostgreSQL
echo "🐘 Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE USER ctfuser WITH PASSWORD 'ctfpassword';" 2>/dev/null || {
    echo "⚠️  Пользователь ctfuser уже существует"
}
sudo -u postgres psql -c "CREATE DATABASE ctfarena OWNER ctfuser;" 2>/dev/null || {
    echo "⚠️  База данных ctfarena уже существует"
}
sudo -u postgres psql -c "ALTER USER ctfuser CREATEDB;" 2>/dev/null || {
    echo "⚠️  Права уже назначены"
}

# Настройка Redis
echo "🔴 Настройка Redis..."
systemctl enable redis-server
systemctl start redis-server

# Создание пользователя для приложения
echo "👤 Создание пользователя приложения..."
if ! id "ctf" &>/dev/null; then
    useradd -m -s /bin/bash ctf
    usermod -aG sudo ctf
    echo "✅ Пользователь ctf создан"
else
    echo "⚠️  Пользователь ctf уже существует"
fi

# Создание системного пользователя для сервисов
if ! id "ctfapp" &>/dev/null; then
    useradd -r -s /bin/false ctfapp
    echo "✅ Системный пользователь ctfapp создан"
else
    echo "⚠️  Пользователь ctfapp уже существует"
fi

# Создание директорий
echo "📁 Создание структуры директорий..."
mkdir -p /opt/ctf-arena/{backend,frontend,logs,backups,uploads}
chown -R ctf:ctf /opt/ctf-arena
chown -R ctfapp:ctfapp /opt/ctf-arena/{logs,backups,uploads}

# Настройка прав
chmod 755 /opt/ctf-arena
chmod 750 /opt/ctf-arena/backups
chmod 755 /opt/ctf-arena/uploads

# Настройка fail2ban для SSH защиты
echo "🛡️  Настройка fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = auto

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Настройка часового пояса
echo "⏰ Настройка времени..."
timedatectl set-timezone Europe/Moscow

# Установка последней версии pip
echo "🐍 Обновление pip..."
python3 -m pip install --upgrade pip

echo "✅ Настройка сервера завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте файлы проекта в /opt/ctf-arena/"
echo "2. Запустите скрипт интеграции: ./integrate_frontend_backend.sh"
echo "3. Запустите деплой: ./deploy_project.sh"
echo ""
echo "⚠️  Предупреждения fail2ban можно игнорировать - это проблемы совместимости с Python 3.12"
