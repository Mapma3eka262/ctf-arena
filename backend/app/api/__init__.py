# backend/app/api/__init__.py
from .auth import router as auth_router
from .users import router as users_router
from .teams import router as teams_router
from .challenges import router as challenges_router
from .submissions import router as submissions_router
from .admin import router as admin_router
from .monitoring import router as monitoring_router
from .websocket import router as websocket_router
from .dynamic_challenges import router as dynamic_challenges_router
from .notifications import router as notifications_router
from .analytics import router as analytics_router
from .audit import router as audit_router

__all__ = [
    'auth_router',
    'users_router',
    'teams_router',
    'challenges_router',
    'submissions_router',
    'admin_router',
    'monitoring_router',
    'websocket_router',
    'dynamic_challenges_router',
    'notifications_router',
    'analytics_router',
    'audit_router'
]