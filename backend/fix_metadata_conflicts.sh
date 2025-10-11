#!/bin/bash
# backend/fix_metadata_conflicts.sh

echo "🔧 Исправление конфликта имен 'metadata'..."

# Создаем резервную копию
cp app/models/notification.py app/models/notification.py.backup

# Исправляем файл
sed -i 's/^[[:space:]]*metadata[[:space:]]*:/    notification_data:/g' app/models/notification.py
sed -i "s/'metadata'/'notification_data'/g" app/models/notification.py

echo "✅ Файл notification.py исправлен"
echo "📝 Создаем новую миграцию..."

source venv/bin/activate
alembic revision --autogenerate -m "rename_metadata_to_notification_data"
alembic upgrade head

echo "🎉 Конфликт исправлен!"
