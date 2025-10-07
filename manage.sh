# Добавьте этот case в существующий скрипт manage.sh

"migrate")
    check_root "migrate"
    log_info "Применение миграций базы данных..."
    cd $BACKEND_DIR
    source $VENV_PATH/bin/activate
    
    if [ -f "alembic.ini" ] && [ -d "alembic" ]; then
        alembic upgrade head
        log_success "Миграции применены"
    else
        log_error "Alembic не настроен"
        exit 1
    fi
    ;;

"create-migration")
    check_root "create-migration"
    message=${2:-"auto migration"}
    log_info "Создание миграции: $message"
    cd $BACKEND_DIR
    source $VENV_PATH/bin/activate
    
    if [ -f "alembic.ini" ] && [ -d "alembic" ]; then
        alembic revision --autogenerate -m "$message"
        log_success "Миграция создана"
    else
        log_error "Alembic не настроен"
        exit 1
    fi
    ;;
