#!/bin/bash

# CyberCTF Arena - Fixed Integration Script for Ubuntu 24.04
set -e

echo "🔗 Интеграция фронтенда и бэкенда (исправленная версия)..."

# Проверка прав
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с правами root"
    exit 1
fi

# Переменные
PROJECT_DIR="/opt/ctf-arena"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
NGINX_DIR="/etc/nginx"

# Проверка существования директорий
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Директория backend не найдена: $BACKEND_DIR"
    echo "Скопируйте файлы backend в эту директорию"
    exit 1
fi

# Создание виртуального окружения Python
echo "🐍 Настройка Python окружения..."
cd $BACKEND_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "⚠️  Виртуальное окружение уже существует"
fi

source venv/bin/activate

# Установка исправленных зависимостей Python
echo "📦 Установка Python зависимостей (исправленные версии)..."
pip install --upgrade pip

# Устанавливаем проблемные зависимости отдельно
echo "🔧 Установка проблемных зависимостей..."
pip install "bcrypt==4.1.1" --no-build-isolation
pip install "dnspython>=2.0.0"
pip install "email-validator==2.1.0"

# Создаем исправленный requirements.txt
cat > requirements_fixed.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dateutil==2.8.2
pydantic==2.5.0
pydantic-settings==2.1.0
celery==5.3.4
redis==5.0.1
requests==2.31.0
python-dotenv==1.0.0
aiofiles==23.2.1
jinja2==3.1.2
pillow==10.1.0
cryptography==41.0.7
dnspython>=2.0.0
EOF

# Устанавливаем исправленные зависимости
if [ -f "requirements_fixed.txt" ]; then
    pip install -r requirements_fixed.txt
    echo "✅ Зависимости установлены"
else
    # Альтернативная установка если файла нет
    pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary
    pip install python-jose passlib python-multipart python-dateutil
    pip install pydantic pydantic-settings celery redis requests
    pip install python-dotenv aiofiles jinja2 pillow cryptography
    pip install dnspython email-validator
    echo "✅ Зависимости установлены (альтернативный метод)"
fi

# Проверяем установку зависимостей
echo "🔍 Проверка установленных пакетов..."
pip list | grep -E "(fastapi|sqlalchemy|psycopg2|celery|redis)"

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."

# Проверка доступности PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL не запущен"
    systemctl start postgresql
    echo "✅ PostgreSQL запущен"
fi

# Используем простой скрипт для инициализации БД
if [ -f "simple_init_db.py" ]; then
    echo "🚀 Запуск simple_init_db.py..."
    python3 simple_init_db.py
else
    # Альтернативный метод с обработкой ошибок
    echo "⚠️  Используем альтернативный метод инициализации..."
    export PYTHONPATH="$BACKEND_DIR"
    
    # Создаем простой скрипт инициализации
    cat > init_db_simple.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import create_engine, text
    from app.core.config import settings
    
    print('🔧 Создание таблиц базы данных...')
    engine = create_engine(settings.DATABASE_URL)
    
    # Простая проверка подключения
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
        print('✅ Подключение к базе данных успешно')
    
    # Импортируем и запускаем стандартную инициализацию
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ Таблицы базы данных созданы')
    
    # Создаем тестового пользователя если нужно
    from app.models.user import User
    from app.models.team import Team
    from app.core.security import get_password_hash
    from sqlalchemy.orm import Session
    
    with Session(engine) as session:
        # Проверяем, есть ли уже пользователи
        existing_user = session.query(User).first()
        if not existing_user:
            print('👤 Создание тестового пользователя...')
            team = Team(name="Test Team")
            session.add(team)
            session.flush()
            
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
                is_captain=True,
                team_id=team.id
            )
            session.add(user)
            session.commit()
            print('✅ Тестовый пользователь создан')
        else:
            print('ℹ️  Пользователи уже существуют')
    
except Exception as e:
    print(f'❌ Ошибка инициализации БД: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('🎉 Инициализация базы данных завершена успешно!')
PYTHON_EOF

    python3 init_db_simple.py
    rm -f init_db_simple.py
fi

# Настройка статических файлов
echo "📁 Настройка статических файлов..."
mkdir -p $BACKEND_DIR/static
chown -R ctfapp:ctfapp $BACKEND_DIR/static

# Копирование frontend файлов (если они существуют)
echo "🌐 Настройка фронтенда..."
if [ -d "./frontend" ]; then
    cp -r ./frontend/* $FRONTEND_DIR/ 2>/dev/null || true
    echo "✅ Файлы фронтенда скопированы"
else
    echo "⚠️  Директория frontend не найдена, пропускаем"
fi

chown -R ctfapp:ctfapp $FRONTEND_DIR 2>/dev/null || true

# Создание сервисных файлов systemd
echo "⚙️ Создание systemd сервисов..."

# Backend API сервис
cat > /etc/systemd/system/ctf-api.service << EOF
[Unit]
Description=CyberCTF Arena API
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Celery worker сервис
cat > /etc/systemd/system/ctf-celery.service << EOF
[Unit]
Description=CyberCTF Arena Celery Worker
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery worker --loglevel=info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Celery beat сервис
cat > /etc/systemd/system/ctf-celery-beat.service << EOF
[Unit]
Description=CyberCTF Arena Celery Beat
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=ctfapp
Group=ctfapp
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
Environment=PYTHONPATH=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/celery -A app.tasks.celery beat --loglevel=info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Настройка прав сервисных файлов
chmod 644 /etc/systemd/system/ctf-*.service

# Перезагрузка systemd
systemctl daemon-reload

# Включение сервисов
systemctl enable ctf-api ctf-celery ctf-celery-beat

echo "✅ Интеграция завершена!"
echo ""
echo "Сервисы созданы и включены:"
echo "  ctf-api.service"
echo "  ctf-celery.service" 
echo "  ctf-celery-beat.service"
echo ""
echo "Для запуска используйте:"
echo "  sudo systemctl start ctf-api ctf-celery ctf-celery-beat"
echo "  sudo systemctl status ctf-api"
