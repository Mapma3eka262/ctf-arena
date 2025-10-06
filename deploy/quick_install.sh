#!/bin/bash

# CyberCTF Arena - Quick Install Script for Ubuntu 24.04
set -e

echo "🎯 Быстрая установка CyberCTF Arena на Ubuntu 24.04"

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo ./quick_install.sh"
    exit 1
fi

# Создание директории проекта
PROJECT_DIR="/opt/ctf-arena"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "📥 Клонирование/копирование проекта..."
# В реальном сценарии здесь будет git clone
# git clone https://github.com/your-org/ctf-arena.git .

echo "🚀 Запуск полной установки..."
chmod +x deploy/*.sh
./deploy/setup_server.sh
./deploy/integrate_frontend_backend.sh  
./deploy/deploy_project.sh

echo ""
echo "🎉 Установка CyberCTF Arena завершена!"
echo ""
echo "🌐 Приложение доступно по адресу: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "🛠️  Управление:"
echo "   sudo $PROJECT_DIR/manage.sh status  - статус сервисов"
echo "   sudo $PROJECT_DIR/manage.sh logs    - просмотр логов"
echo "   sudo $PROJECT_DIR/manage.sh backup  - бэкап БД"
echo ""
echo "⚠️  Дополнительные шаги:"
echo "   1. Настройте доменное имя и SSL"
echo "   2. Измените секретные ключи в настройках"
echo "   3. Настройте почтовый сервис для уведомлений"