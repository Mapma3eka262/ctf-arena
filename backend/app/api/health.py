# backend/app/api/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "docker": await check_docker(),
            "microservices": await microservice_manager.health_check()
        },
        "metrics": {
            "active_connections": websocket_manager.active_connections,
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent()
        }
    }