# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio

from app.core.config import settings
from app.core.database import init_db
from app.core.microservices import microservice_manager, AuthService, ScoringService
from app.api.websocket import manager as websocket_manager
from app.plugins import plugin_manager
from app.utils.docker_manager import DockerManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Запуск CyberCTF Arena...")
    
    # Инициализация базы данных
    init_db()
    
    # Регистрация микросервисов
    microservice_manager.register_service("auth", AuthService())
    microservice_manager.register_service("scoring", ScoringService())
    await microservice_manager.initialize()
    
    # Загрузка плагинов
    plugin_modules = plugin_manager.discover_plugins()
    for module in plugin_modules:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith('Plugin') and 
                attr_name != 'BasePlugin'):
                plugin_manager.load_plugin(attr)
    
    # Инициализация Docker менеджера
    docker_manager = DockerManager()
    
    # Запуск фоновых задач
    asyncio.create_task(background_tasks())
    
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} запущен")
    
    yield
    
    # Shutdown
    print("🛑 Остановка CyberCTF Arena...")
    
    await websocket_manager.disconnect_all()
    await microservice_manager.shutdown()
    
    # Выгрузка плагинов
    for plugin_name in list(plugin_manager.loaded_plugins.keys()):
        plugin_manager.unload_plugin(plugin_name)
    
    print("✅ Приложение остановлено")

async def background_tasks():
    """Фоновые задачи приложения"""
    while True:
        try:
            # Проверка здоровья сервисов каждые 30 секунд
            health_status = await microservice_manager.health_check()
            
            # Очистка устаревших данных
            await cleanup_old_data()
            
            # Обновление статистики
            await update_system_stats()
            
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Ошибка в фоновых задачах: {e}")
            await asyncio.sleep(60)

async def cleanup_old_data():
    """Очистка устаревших данных"""
    # Здесь будет логика очистки старых данных
    pass

async def update_system_stats():
    """Обновление системной статистики"""
    # Здесь будет логика обновления статистики
    pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CTF платформа для киберсоревнований с улучшенной архитектурой",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов API
from app.api import (
    auth, users, teams, challenges, submissions, 
    admin, monitoring, websocket, dynamic_challenges,
    notifications, analytics
)

app.include_router(auth.router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(users.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(teams.router, prefix="/api/teams", tags=["Команды"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["Задания"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Отправки"])
app.include_router(admin.router, prefix="/api/admin", tags=["Администрирование"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Мониторинг"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])
app.include_router(dynamic_challenges.router, prefix="/api/dynamic", tags=["Динамические задания"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Уведомления"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Аналитика"])

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": f"Добро пожаловать в {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Расширенная проверка здоровья приложения"""
    from app.core.cache import cache_manager
    from app.core.database import engine
    import psutil
    import os
    
    # Проверка базы данных
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Проверка Redis
    cache_status = "healthy"
    try:
        cache_manager.set("health_check", "test", 10)
        if cache_manager.get("health_check") != "test":
            cache_status = "error"
    except Exception as e:
        cache_status = f"error: {str(e)}"
    
    # Системные метрики
    system_metrics = {
        "memory_usage": f"{psutil.virtual_memory().percent:.1f}%",
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "disk_usage": f"{psutil.disk_usage('/').percent:.1f}%",
        "process_memory": f"{psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.1f} MB"
    }
    
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": settings.APP_VERSION,
        "services": {
            "database": db_status,
            "cache": cache_status,
            "microservices": await microservice_manager.health_check(),
            "websocket": {
                "active_connections": len(websocket_manager.active_connections),
                "connected_teams": len(websocket_manager.team_connections)
            }
        },
        "system": system_metrics,
        "plugins": {
            "loaded": len(plugin_manager.loaded_plugins),
            "list": plugin_manager.get_loaded_plugins()
        }
    }

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    """Обработчик 404 ошибок"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"}
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    """Обработчик 500 ошибок"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )