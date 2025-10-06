from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api import (
    auth, users, teams, challenges, 
    submissions, admin, monitoring
)

# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CTF платформа для киберсоревнований",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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
app.include_router(auth.router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(users.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(teams.router, prefix="/api/teams", tags=["Команды"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["Задания"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Отправки"])
app.include_router(admin.router, prefix="/api/admin", tags=["Администрирование"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Мониторинг"])

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    init_db()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} запущен")

@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    print("Приложение остановлено")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": f"Добро пожаловать в {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",  # В реальности datetime.utcnow().isoformat()
        "version": settings.APP_VERSION
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