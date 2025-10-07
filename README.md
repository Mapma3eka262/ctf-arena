# CyberCTF Arena

![CyberCTF Arena](https://img.shields.io/badge/Platform-CTF-red)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Полнофункциональная платформа для проведения CTF (Capture The Flag) соревнований в формате Attack-Defense. Система поддерживает многопользовательские команды, автоматическую проверку флагов, мониторинг сервисов и многоязычный интерфейс.

## 🚀 Возможности

### Основные функции
- **🛡️ Аутентификация и авторизация** - JWT токены, ролевая модель (admin/captain/member)
- **👥 Управление командами** - Регистрация, приглашения, управление участниками
- **🎯 Система заданий** - Категории WEB, Crypto, Forensics, Reversing, PWN, MISC
- **🚩 Проверка флагов** - Автоматическая валидация, первая кровь, начисление очков
- **📊 Мониторинг сервисов** - Автоматическая проверка доступности, история статусов
- **⏰ Таймер соревнований** - Гибкая система времени, продление с штрафами
- **🌍 Многоязычность** - Полная поддержка русского и английского языков
- **📱 Адаптивный интерфейс** - Современный веб-интерфейс для всех устройств

### Технические особенности
- **🔧 Микросервисная архитектура** - FastAPI, Celery, Redis
- **📈 Масштабируемость** - Поддержка до 50 одновременных пользователей
- **🔒 Безопасность** - Хеширование паролей, валидация данных, CORS
- **📨 Уведомления** - Email и Telegram уведомления
- **🐳 Контейнеризация** - Полная поддержка Docker
- **📊 Аналитика** - Подробная статистика и отчеты

## 🏗️ Архитектура проекта
```
cyberctf-arena/
├── 📁 backend/ # Бэкенд приложение
│ ├── 📁 app/
│ │ ├── 📁 api/ # API endpoints
│ │ │ ├── auth.py # Аутентификация
│ │ │ ├── users.py # Пользователи
│ │ │ ├── teams.py # Команды
│ │ │ ├── challenges.py # Задания
│ │ │ ├── submissions.py # Отправки флагов
│ │ │ ├── admin.py # Администрирование
│ │ │ └── monitoring.py # Мониторинг
│ │ ├── 📁 core/ # Основные компоненты
│ │ │ ├── config.py # Конфигурация
│ │ │ ├── security.py # Безопасность
│ │ │ ├── database.py # База данных
│ │ │ ├── auth.py # Аутентификация
│ │ │ └── i18n.py # Локализация
│ │ ├── 📁 models/ # Модели данных
│ │ │ ├── user.py # Пользователи
│ │ │ ├── team.py # Команды
│ │ │ ├── challenge.py # Задания
│ │ │ ├── submission.py # Отправки
│ │ │ ├── service.py # Сервисы
│ │ │ ├── invitation.py # Приглашения
│ │ │ └── competition.py # Соревнования
│ │ ├── 📁 schemas/ # Pydantic схемы
│ │ │ ├── auth.py # Аутентификация
│ │ │ ├── user.py # Пользователи
│ │ │ ├── team.py # Команды
│ │ │ ├── challenge.py # Задания
│ │ │ └── submission.py # Отправки
│ │ ├── 📁 services/ # Бизнес-логика
│ │ │ ├── auth_service.py # Аутентификация
│ │ │ ├── email_service.py # Email
│ │ │ ├── telegram_service.py # Telegram
│ │ │ ├── monitoring_service.py # Мониторинг
│ │ │ ├── flag_service.py # Флаги
│ │ │ ├── scoring_service.py # Очки
│ │ │ ├── invitation_service.py # Приглашения
│ │ │ └── competition_service.py # Соревнования
│ │ ├── 📁 tasks/ # Фоновые задачи
│ │ │ ├── celery.py # Celery конфигурация
│ │ │ ├── email_tasks.py # Email задачи
│ │ │ ├── monitoring_tasks.py # Мониторинг
│ │ │ ├── invitation_tasks.py # Приглашения
│ │ │ └── cleanup_tasks.py # Очистка
│ │ ├── 📁 utils/ # Вспомогательные утилиты
│ │ │ ├── validators.py # Валидаторы
│ │ │ └── helpers.py # Хелперы
│ │ └── main.py # Основное приложение
│ ├── 📁 migrations/ # Миграции базы данных
│ │ ├── versions/ # Версии миграций
│ │ ├── env.py # Окружение Alembic
│ │ └── script.py.mako # Шаблон миграций
│ ├── requirements.txt # Зависимости Python
│ ├── Dockerfile # Docker образ
│ └── celery_config.py # Конфигурация Celery
├── 📁 frontend/ # Фронтенд приложение
│ ├── index.html # Главная страница
│ ├── lk.html # Личный кабинет
│ ├── arena.html # Арена соревнований
│ ├── admin.html # Административная панель
│ └── assets/ # Статические ресурсы
├── 📁 deploy/ # Скрипты развертывания
│ ├── setup_server.sh # Подготовка сервера
│ ├── integrate_frontend_backend.sh # Интеграция
│ ├── deploy_project.sh # Развертывание проекта
│ ├── quick_install.sh # Быстрая установка
│ └── nginx.conf # Конфигурация nginx
├── docker-compose.yml # Docker Compose
├── manage.sh # Скрипт управления
└── README.md # Документация
```

## 📋 Требования

### Системные требования
- **ОС**: Ubuntu 24.04
- **Память**: 2 GB RAM минимум
- **Диск**: 10 GB свободного места
- **Процессор**: 2+ ядра

### Программное обеспечение
- **Python**: 3.11+
- **PostgreSQL**: 13+
- **Redis**: 7+
- **Nginx**: 1.18+
- **Docker**: 20.10+ (опционально)

## 🛠️ Установка

### Установка
1. Подготовка сервера
```bash
cd /opt/
sudo git clone https://github.com/Mapma3eka262/cyberctf-arena.git
cd ctf-arena/deploy
sudo chmod +x *.sh
sudo ./setup_server.sh
```

2. Интеграция компонентов
```bash
sudo ./integrate_frontend_backend.sh
```

3. Развертывание проекта
```bash
sudo ./deploy_project.sh
```

### Docker установка
```bash
# Клонируйте репозиторий
git clone https://github.com/Mapma3eka262/cyberctf-arena.git
cd cyberctf-arena

# Запустите через Docker Compose
docker-compose up -d

# Или соберите и запустите
docker-compose build
docker-compose up -d
```

## ⚙️ Конфигурация

### Основные настройки (.env)
```ini
# База данных
DATABASE_URL=postgresql://cyberctf:cyberctf2025@localhost:5432/cyberctf

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (обязательно для работы)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@cyberctf.ru

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id

# Приложение
FRONTEND_URL=http://your-domain.com
MAX_TEAM_SIZE=5
```

### Настройка сервисов

После установки проверьте статус сервисов:
```bash
# Просмотр статуса
/home/cyberctf/cyberctf-arena/manage.sh status

# Или через systemctl
sudo systemctl status cyberctf-backend
sudo systemctl status cyberctf-celery
sudo systemctl status cyberctf-celerybeat
sudo systemctl status nginx
```
## 🎮 Использование

### Доступ к системе
- **Главная страница**: http://your-server-ip
- **Личный кабинет**: http://your-server-ip/lk.html
- **Арена CTF**: http://your-server-ip/arena.html
- **Админ-панель**: http://your-server-ip/admin.html
- **API документация**: http://your-server-ip/docs

### Учетные записи по умолчанию
- **Администратор**:
  - Логин: admin
  - Пароль: admin123
  - Email: admin@cyberctf.ru

### Управление системой
```bash
# Используйте скрипт управления
cd /home/cyberctf/cyberctf-arena

# Запуск/остановка
./manage.sh start    # Запустить все сервисы
./manage.sh stop     # Остановить все сервисы
./manage.sh restart  # Перезапустить все сервисы

# Мониторинг
./manage.sh status   # Статус сервисов
./manage.sh logs     # Логи бэкенда
./manage.sh celery-logs  # Логи Celery

# Администрирование
./manage.sh backup   # Создать резервную копию
./manage.sh update   # Обновить приложение
./manage.sh shell    # Открыть shell БД
```

## 📚 API Endpoints
### Аутентификация
- ```POST /api/auth/register``` - Регистрация команды
- ```POST /api/auth/login``` - Вход в систему
- ```POST /api/auth/verify-email``` - Подтверждение email
- ```POST /api/auth/refresh``` - Обновление токена

### Пользователи
- ```GET /api/users/me``` - Профиль текущего пользователя
- ```GET /api/users/me/team``` - Информация о команде

### Команды
- ```GET /api/teams/my``` - Моя команда
- ```GET /api/teams/ranking``` - Рейтинг команд
- ```POST /api/teams/invites``` - Приглашение участника

### Задания
- ```GET /api/challenges``` - Список заданий
- ```GET /api/challenges/{id}``` - Информация о задании
- ```GET /api/challenges/categories``` - Список категорий

### Отправки флагов
- ```POST /api/submissions``` - Отправить флаг
- ```GET /api/submissions``` - История отправок
- ```GET /api/submissions/stats``` - Статистика

### Мониторинг
- ```GET /api/monitoring/services``` - Статус сервисов
- ```GET /api/monitoring/history``` - История статусов

### Администрирование
- ```GET /api/admin/dashboard``` - Данные дашборда
- ```POST /api/admin/challenges``` - Создание задания
- ```POST /api/admin/competition/start``` - Начало соревнования

## 🗃️ Модели данных
### User
```python 
id: int
username: str
email: str
password_hash: str
role: str  # 'admin', 'captain', 'member'
team_id: int
language: str  # 'ru', 'en'
is_active: bool
email_verified: bool
```

### Team
```python 
id: int
name: str
score: int
ip_address: str
registration_date: datetime
is_active: bool
captain_id: int
penalty_minutes: int
```

### Challenge
```python 
id: int
title: str
category: str  # 'WEB', 'Crypto', 'Forensics', 'Reversing', 'PWN', 'MISC'
points: int
description: str
flag: str
is_active: bool
```

### Submission
```python 
id: int
user_id: int
team_id: int
challenge_id: int
flag: str
status: str  # 'pending', 'accepted', 'rejected'
points_awarded: int
is_first_blood: bool
```

## 🔧 Разработка
### Локальная разработка
```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/cyberctf-arena.git
cd cyberctf-arena/backend

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте окружение
cp .env.example .env
# Отредактируйте .env файл

# Запустите миграции
alembic upgrade head

# Запустите сервер разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запустите Celery worker
celery -A app.tasks.celery worker --loglevel=info

# Запустите Celery beat
celery -A app.tasks.celery beat --loglevel=info
```

### Docker разработка
```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up --build

# Просмотр логов
docker-compose logs -f backend
```

## 📊 Мониторинг и логи
### Логи приложения
```bash
# Логи бэкенда
sudo journalctl -u cyberctf-backend -f

# Логи Celery
sudo journalctl -u cyberctf-celery -f

# Логи nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Метрики здоровья
- ```GET /health``` - Health check endpoint
- Статус сервисов через systemd
- Мониторинг базы данных и Redis

## 🔒 Безопасность
## Рекомендации по безопасности
1. Измените пароли по умолчанию
2. Настройте SSL/TLS сертификаты
3. Ограничьте доступ к административным интерфейсам
4. Регулярно обновляйте зависимости
5. Настройте брандмауэр
6. Используйте сильные секретные ключи

### Конфигурация брандмауэра
```bash
# Открыть только необходимые порты
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## 🐛 Устранение неисправностей
### Распространенные проблемы

Сервисы не запускаются:
```bash 
# Проверьте статус
sudo systemctl status cyberctf-backend

# Просмотрите логи
sudo journalctl -u cyberctf-backend -f
```


Проблемы с базой данных:
```bash 
# Проверьте подключение
sudo -u postgres psql -d cyberctf -c "SELECT 1;"

# Перезапустите миграции
cd /home/cyberctf/cyberctf-arena/backend
source venv/bin/activate
alembic downgrade base
alembic upgrade head
```


Проблемы с Redis:
```bash
# Проверьте статус Redis
sudo systemctl status redis

# Проверьте подключение
redis-cli ping
```

### Восстановление из резервной копии
```bash
# Создание резервной копии
/home/cyberctf/cyberctf-arena/manage.sh backup

# Восстановление из резервной копии
sudo -u postgres psql cyberctf < /path/to/backup.sql
```

## 🤝 Вклад в проект
Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте feature branch (git checkout -b feature/AmazingFeature)
3. Закоммитьте изменения (git commit -m 'Add some AmazingFeature')
4. Запушьте в ветку (git push origin feature/AmazingFeature)
5. Откройте Pull Request

## 📄 Лицензия
Этот проект распространяется под лицензией MIT. Смотрите файл ```LICENSE``` для получения дополнительной информации.

## 🙏 Благодарности

- Команда разработчиков CyberCTF Arena
- Сообщество CTF энтузиастов
- Все контрибьюторы и тестеры

#### CyberCTF Arena - мощная платформа для проведения кибербезопасностных соревнований. 🚀
Сделано с ❤️ для сообщества CTF









