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
# HTTP редирект на HTTPS
server {
    listen 80;
    server_name ctfarena.scanbit.ru;
    
    # Редирект всех HTTP запросов на HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name ctfarena.scanbit.ru;
    
    # SSL сертификаты
    ssl_certificate /etc/nginx/ssl/ctfarena/ctfarena.crt;
    ssl_certificate_key /etc/nginx/ssl/ctfarena/ctfarena.key;
    
    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    
    # Директория с фронтендом
    root /opt/ctf-arena/frontend;
    index index.html;

    # Статические файлы
    location /static/ {
        alias /opt/ctf-arena/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Безопасность
        add_header X-Content-Type-Options "nosniff";
    }

    location /assets/ {
        alias /opt/ctf-arena/frontend/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Безопасность
        add_header X-Content-Type-Options "nosniff";
    }

    # API прокси
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # Таймауты
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket прокси
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты для WebSocket
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 86400;
    }

    # HTML страницы
    location / {
        try_files $uri $uri/ /index.html;

        # Кэширование HTML
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
        
        # Безопасность
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
    }

    # Загрузки файлов
    location /uploads/ {
        alias /opt/ctf-arena/uploads/;
        expires 1h;
        add_header Cache-Control "public";
        
        # Безопасность загрузок
        add_header X-Content-Type-Options "nosniff";
        
        # Ограничение размера загружаемых файлов
        client_max_body_size 100M;
    }

    # Безопасность - скрываем системные файлы
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ /\.env {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ /\.git {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ /\.ht {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Обработка ошибок
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
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
