#!/bin/bash
# setup_ssl.sh

set -e

echo "🔐 Настройка SSL для CTF Arena..."

# Создаем директории
sudo mkdir -p /etc/nginx/ssl/ctfarena
sudo mkdir -p /opt/ctf-arena/uploads

# Генерируем сертификат
echo "📝 Генерация самоподписанного SSL сертификата..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/ctfarena/ctfarena.key \
    -out /etc/nginx/ssl/ctfarena/ctfarena.crt \
    -subj "/C=RU/ST=Kurgna/L=Kurgan/O=Scanbit/OU=IT Department/CN=ctfarena.scanbit.ru"

# Устанавливаем права
sudo chmod 600 /etc/nginx/ssl/ctfarena/ctfarena.key
sudo chmod 644 /etc/nginx/ssl/ctfarena/ctfarena.crt

# Обновляем конфигурацию nginx
echo "📁 Обновление конфигурации nginx..."

# Создаем бэкап оригинальной конфигурации
sudo cp /etc/nginx/sites-available/ctf-arena /etc/nginx/sites-available/ctf-arena.backup

# Записываем новую конфигурацию
sudo tee /etc/nginx/sites-available/ctf-arena > /dev/null << 'EOF'
# Вставьте сюда обновленную конфигурацию сайта из шага 3
EOF

# Проверяем конфигурацию nginx
echo "🔍 Проверка конфигурации nginx..."
sudo nginx -t

# Перезапускаем nginx
echo "🔄 Перезапуск nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ SSL настроен успешно!"
echo ""
echo "📋 Информация о сертификате:"
echo "   Сертификат: /etc/nginx/ssl/ctfarena/ctfarena.crt"
echo "   Ключ:       /etc/nginx/ssl/ctfarena/ctfarena.key"
echo ""
echo "⚠️  ВАЖНО: Это самоподписанный сертификат!"
echo "   Браузер будет показывать предупреждение о безопасности."
echo "   Для продакшена рекомендуется использовать Let's Encrypt."
echo ""
echo "🌐 Сайт доступен по адресам:"
echo "   HTTP:  http://ctfarena.scanbit.ru (редирект на HTTPS)"
echo "   HTTPS: https://ctfarena.scanbit.ru"
