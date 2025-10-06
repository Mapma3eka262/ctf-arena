setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    cd $BACKEND_DIR
    
    detect_os
    
    # ... остальной код ...
    
    # Устанавливаем зависимости в зависимости от ОС
    if [ "$OS_ID" == "centos" ] || [ "$OS_ID" == "rhel" ]; then
        log_info "Installing CentOS-compatible dependencies..."
        pip install \
            redis==4.5.0 \
            python-dateutil==2.8.2 \
            httpx==0.24.0 \
            aiofiles==22.1.0 \
            python-i18n==0.3.9 \
            email-validator==1.3.1 \
            pydantic==1.10.2 \
            pydantic-settings==2.0.3 \
            fastapi==0.95.2 \
            uvicorn==0.21.1 \
            python-multipart==0.0.6 \
            passlib[bcrypt]==1.7.4 \
            python-jose[cryptography]==3.3.0 \
            sqlalchemy==1.4.46 \
            alembic==1.10.2 \
            celery==5.2.7 \
            python-telegram-bot==20.3 \
            psycopg2-binary==2.9.6
    else
        log_info "Installing Ubuntu-compatible dependencies..."
        pip install \
            redis==5.0.1 \
            python-dateutil==2.8.2 \
            httpx==0.25.2 \
            aiofiles==23.2.1 \
            python-i18n==0.3.9 \
            email-validator==2.1.0 \
            pydantic==2.5.0 \
            pydantic-settings==2.1.0 \
            fastapi==0.104.1 \
            uvicorn==0.24.0 \
            python-multipart==0.0.6 \
            passlib[bcrypt]==1.7.4 \
            python-jose[cryptography]==3.3.0 \
            sqlalchemy==2.0.23 \
            alembic==1.12.1 \
            celery==5.3.4 \
            python-telegram-bot==20.7 \
            psycopg2-binary==2.9.9
    fi
    
    # ... остальной код ...
}
