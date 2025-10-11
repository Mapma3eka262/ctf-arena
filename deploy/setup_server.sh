#!/bin/bash
# deploy/setup_server.sh

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
    net-tools \
    docker.io \
    docker-compose

# Настройка Docker
echo "🐳 Настройка Docker..."
systemctl enable docker
systemctl start docker
usermod -aG docker $SUDO_USER

# Настройка брандмауэра
echo "🔥 Настройка брандмауэра..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000
ufw allow 8001
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
mkdir -p /opt/ctf-arena/{backend,frontend,logs,backups,uploads,challenges,ssl}
chown -R ctf:ctf /opt/ctf-arena
chown -R ctfapp:ctfapp /opt/ctf-arena/{logs,backups,uploads}

# Настройка прав
chmod 755 /opt/ctf-arena
chmod 750 /opt/ctf-arena/backups
chmod 755 /opt/ctf-arena/uploads

# Настройка лог-ротации
echo "📝 Настройка лог-ротации..."
cat > /etc/logrotate.d/ctf-arena << EOF
/opt/ctf-arena/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

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
echo "🔧 Дополнительные настройки:"
echo "   - Настройте SSL сертификаты: certbot --nginx"
echo "   - Настройте мониторинг (опционально)"
echo "   - Настройте резервное копирование"