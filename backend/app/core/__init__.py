# backend/app/core/__init__.py
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, get_db
from app.core.security import (
    verify_password, get_password_hash, 
    create_access_token, validate_flag_format
)
from app.core.auth import get_current_user, get_current_admin, get_current_user_ws
from app.core.microservices import microservice_manager, BaseMicroservice
from app.core.cache import cache_manager, cached, invalidate_cache
from app.core.rate_limiting import rate_limiter, rate_limit
from app.core.metrics import (
    REQUEST_COUNT, REQUEST_DURATION, ACTIVE_USERS,
    ACTIVE_CONNECTIONS, SUBMISSION_COUNT, metrics_endpoint
)

__all__ = [
    'settings',
    'Base', 'engine', 'SessionLocal', 'get_db',
    'verify_password', 'get_password_hash', 'create_access_token', 'validate_flag_format',
    'get_current_user', 'get_current_admin', 'get_current_user_ws',
    'microservice_manager', 'BaseMicroservice',
    'cache_manager', 'cached', 'invalidate_cache',
    'rate_limiter', 'rate_limit',
    'REQUEST_COUNT', 'REQUEST_DURATION', 'ACTIVE_USERS',
    'ACTIVE_CONNECTIONS', 'SUBMISSION_COUNT', 'metrics_endpoint'
]