#!/bin/bash
# deploy/integrate_frontend_backend.sh

set -e

echo "🔗 Интеграция фронтенда и бэкенда CyberCTF Arena..."

PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Проверка существования директорий
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Директория бэкенда не найдена: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Директория фронтенда не найдена: $FRONTEND_DIR"
    exit 1
fi

# Создание символических ссылок для разработки
echo "📁 Создание символических ссылок..."

# Статические файлы бэкенда
if [ ! -L "$BACKEND_DIR/static" ]; then
    ln -s "$FRONTEND_DIR/static" "$BACKEND_DIR/static"
    echo "✅ Создана ссылка на статические файлы"
fi

# HTML шаблоны
if [ ! -L "$BACKEND_DIR/app/templates" ]; then
    ln -s "$FRONTEND_DIR/pages" "$BACKEND_DIR/app/templates"
    echo "✅ Создана ссылка на HTML шаблоны"
fi

# Настройка Nginx для обслуживания статических файлов
echo "🌐 Настройка Nginx..."

cat > /etc/nginx/sites-available/ctf-arena << 'EOF'
server {
    listen 80;
    server_name _;
    root /opt/ctf-arena/frontend;
    index index.html;

    # Статические файлы
    location /static/ {
        alias /opt/ctf-arena/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /assets/ {
        alias /opt/ctf-arena/frontend/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API прокси
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket прокси
    location /api/ws/ {
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
    }

    # HTML страницы
    location / {
        try_files $uri $uri/ /index.html;
        
        # Кэширование HTML
        expires 1h;
        add_header Cache-Control "public";
    }

    # Загрузки файлов
    location /uploads/ {
        alias /opt/ctf-arena/uploads/;
        expires 1h;
        add_header Cache-Control "public";
    }

    # Безопасность
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
}
EOF

# Активация сайта
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

if [ ! -L /etc/nginx/sites-enabled/ctf-arena ]; then
    ln -s /etc/nginx/sites-available/ctf-arena /etc/nginx/sites-enabled/
fi

# Проверка конфигурации Nginx
echo "🔧 Проверка конфигурации Nginx..."
nginx -t

# Перезагрузка Nginx
echo "🔄 Перезагрузка Nginx..."
systemctl reload nginx

# Создание сервисных файлов для systemd
echo "🎯 Создание systemd сервисов..."

# Сервис для основного API
cat > /etc/systemd/system/ctf-api.service << EOF
[Unit]
Description=CyberCTF Arena API
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=/opt/ctf-arena/backend
Environment=PATH=/opt/ctf-arena/backend/venv/bin
ExecStart=/opt/ctf-arena/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Сервис для WebSocket
cat > /etc/systemd/system/ctf-websocket.service << EOF
[Unit]
Description=CyberCTF Arena WebSocket
After=network.target ctf-api.service
Requires=ctf-api.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=/opt/ctf-arena/backend
Environment=PATH=/opt/ctf-arena/backend/venv/bin
ExecStart=/opt/ctf-arena/backend/venv/bin/uvicorn app.ws_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Сервис для Celery worker
cat > /etc/systemd/system/ctf-celery.service << EOF
[Unit]
Description=CyberCTF Arena Celery Worker
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=/opt/ctf-arena/backend
Environment=PATH=/opt/ctf-arena/backend/venv/bin
ExecStart=/opt/ctf-arena/backend/venv/bin/celery -A app.tasks.celery worker --loglevel=info
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Сервис для Celery beat
cat > /etc/systemd/system/ctf-celery-beat.service << EOF
[Unit]
Description=CyberCTF Arena Celery Beat
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=/opt/ctf-arena/backend
Environment=PATH=/opt/ctf-arena/backend/venv/bin
ExecStart=/opt/ctf-arena/backend/venv/bin/celery -A app.tasks.celery beat --loglevel=info
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
systemctl daemon-reload

echo "✅ Интеграция завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте переменные окружения в /opt/ctf-arena/.env"
echo "2. Запустите сервисы: systemctl start ctf-api ctf-websocket ctf-celery ctf-celery-beat"
echo "3. Включите автозапуск: systemctl enable ctf-api ctf-websocket ctf-celery ctf-celery-beat"
echo "4. Настройте SSL: certbot --nginx -d your-domain.com"