# README.md
# 🚀 CyberCTF Arena

Современная платформа для проведения CTF-соревнований с улучшенной архитектурой, реальным временем и динамическими заданиями.

## 🌟 Особенности

- **🏗️ Микросервисная архитектура** - Масштабируемая и отказоустойчивая
- **⚡ Реальное время** - WebSocket для мгновенных обновлений
- **🐳 Динамические задания** - Изолированные Docker контейнеры
- **📊 Расширенная аналитика** - Статистика и рекомендации для команд
- **🔌 Система плагинов** - Легко расширяемая функциональность
- **🛡️ Безопасность** - Аудит, rate limiting, защита от атак
- **📱 Адаптивный дизайн** - Работает на всех устройствах

## 🏗️ Архитектура
```
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Frontend │ │ Nginx Proxy │ │ Backend API │
│ (HTML/JS/CSS) │◄──►│ (Port 80/443) │◄──►│ (FastAPI) │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ WebSocket │ │ PostgreSQL │ │ Redis │
│ (Port 8001) │ │ (Database) │ │ (Cache/MQ) │
└─────────────────┘ └──────────────────┘ └─────────────────┘
```

## 🚀 Быстрый старт

### 1. Установка на сервер
```bash
# Клонирование проекта
git clone https://github.com/Mapma3eka262/ctf-arena.git /opt/ctf-arena

# Настройка сервера
cd /opt/ctf-arena/deploy
chmod +x *.sh
sudo ./setup_server.sh

# Настройка окружения
sudo ./setup_env.sh

# Интеграция компонентов
sudo ./integrate_frontend_backend.sh

# Добавляем пользователя ctfapp в группу docker
sudo usermod -aG docker ctfapp

# Перезапускаем сервисы
sudo systemctl daemon-reload
sudo systemctl restart ctf-api ctf-websocket

# Проверяем права
sudo chmod 666 /var/run/docker.sock

# Деплой проекта
sudo ./deploy_project.sh
```

### 2. Локальная разработка
```bash
# Бэкенд
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt

# Инициализация БД
python simple_init_db.py

# Запуск
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (в другом терминале)
cd frontend
python -m http.server 3000
```


## 📁 Структура проекта
```text
ctf-arena/
├── 📁 backend/                 # FastAPI бэкенд
│   ├── 📁 app/                # Основное приложение
│   ├── 📁 migrations/         # Миграции базы данных
│   └── requirements.txt       # Зависимости Python
├── 📁 frontend/               # HTML/CSS/JS фронтенд
│   ├── 📁 assets/            # Статические ресурсы
│   ├── 📁 components/         # Переиспользуемые компоненты
│   └── 📁 pages/             # Страницы приложения
├── 📁 deploy/                 # Скрипты развертывания
└── 📁 challenges/            # Динамические задания
```

## 🔧 Управление
Используйте скрипт управления для основных операций:

```bash
# Статус сервисов
sudo /opt/ctf-arena/manage.sh status

# Запуск/остановка
sudo /opt/ctf-arena/manage.sh start
sudo /opt/ctf-arena/manage.sh stop

# Просмотр логов
sudo /opt/ctf-arena/manage.sh logs api

# Бэкап БД
sudo /opt/ctf-arena/manage.sh backup

# Мониторинг
sudo /opt/ctf-arena/manage.sh monitor
```

## 🎯 API Документация
После запуска доступны:

- **API Docs:** http://localhost:8000/api/docs

- **ReDoc:** http://localhost:8000/api/redoc

- **Health Check:** http://localhost:8000/api/health

## 🔐 Безопасность

- JWT аутентификация
- Rate limiting
- SQL injection protection
- XSS protection
- Audit logging
- Docker isolation для заданий

## 📈 Мониторинг

- Prometheus метрики на порту 9090
- Health checks всех сервисов
- Real-time статистика подключений
- Логи аудита безопасности

## 🐳 Docker
Запуск в Docker:

```bash
cd /opt/ctf-arena
docker-compose -f docker-compose.microservices.yml up -d
```

## 🤝 Разработка
### Добавление нового API endpoint

1. Создайте файл в ```app/api/```
2. Добавьте router в ```app/main.py```
3. Создайте схемы в ```app/schemas/```
4. обавьте бизнес-логику в ```app/services/```

### Создание динамического задания

1. Создайте Docker образ задания
2. Добавьте запись в таблицу ```challenges```
3. Создайте конфигурацию в ```dynamic_challenges```

## 🐛 Поиск проблем
```bash
# Проверка структуры
python check_structure.py

# Проверка зависимостей
pip check

# Просмотр логов
journalctl -u ctf-api -f
```

## 📄 Лицензия
MIT License - смотрите файл LICENSE для деталей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Добавьте тесты
5. Отправьте pull request

## 📞 Поддержка
Документация: ```/docs/```

Issues: GitHub Issues

Email: support@ctf-arena.local

CyberCTF Arena - современная платформа для киберсоревнований 🏆
