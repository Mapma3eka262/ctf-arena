# backend/app/api/monitoring.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import psutil
import docker
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.schemas.user import UserResponse 
from app.models.service import Service
from app.services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    try:
        # Проверка использования ресурсов
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Проверка Docker
        docker_client = docker.from_env()
        docker_info = docker_client.info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available // (1024**3)}GB",
                "disk_usage": f"{disk.percent}%",
                "disk_free": f"{disk.free // (1024**3)}GB"
            },
            "docker": {
                "containers_running": docker_info['ContainersRunning'],
                "containers_total": docker_info['Containers'],
                "images_count": docker_info['Images']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/services")
async def get_services_status(
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение статуса всех сервисов"""
    monitoring_service = MonitoringService(db)
    services = db.query(Service).filter(Service.is_active == True).all()
    
    results = []
    for service in services:
        status = monitoring_service.check_service_status(service)
        results.append({
            "id": service.id,
            "name": service.name,
            "type": service.type,
            "host": service.host,
            "port": service.port,
            "status": status,
            "response_time": service.response_time,
            "last_checked": service.last_checked,
            "error_message": service.error_message
        })
    
    return {
        "services": results,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/services/{service_id}/check")
async def check_service(
    service_id: int,
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Принудительная проверка конкретного сервиса"""
    monitoring_service = MonitoringService(db)
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден")
    
    status = monitoring_service.check_service_status(service)
    
    return {
        "service_id": service.id,
        "name": service.name,
        "status": status,
        "response_time": service.response_time,
        "last_checked": service.last_checked
    }

@router.get("/metrics")
async def get_system_metrics(
    current_user: UserResponse = Depends(get_current_admin)
):
    """Получение системных метрик"""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Memory
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    
    # Network
    net_io = psutil.net_io_counters()
    
    # Processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Сортируем процессы по использованию CPU
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "cores": cpu_count,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        },
        "top_processes": processes[:10]  # Топ 10 процессов по CPU
    }

@router.get("/database")
async def get_database_stats(
    current_user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение статистики базы данных"""
    try:
        # Размер базы данных
        db_size = db.execute("SELECT pg_database_size('ctfarena')").scalar()
        
        # Количество записей в таблицах
        tables = ['users', 'teams', 'challenges', 'submissions', 'services']
        table_stats = {}
        
        for table in tables:
            count = db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
            table_stats[table] = count
        
        # Активные подключения
        active_connections = db.execute(
            "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'ctfarena'"
        ).scalar()
        
        # Статистика по индексам
        index_stats = db.execute("""
            SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
            FROM pg_stat_user_indexes 
            ORDER BY idx_scan DESC 
            LIMIT 10
        """).fetchall()
        
        return {
            "database_size_bytes": db_size,
            "database_size_human": f"{db_size // (1024**2)} MB",
            "table_stats": table_stats,
            "active_connections": active_connections,
            "top_indexes": [
                {
                    "schema": row[0],
                    "table": row[1],
                    "index": row[2],
                    "scans": row[3],
                    "tuples_read": row[4],
                    "tuples_fetched": row[5]
                }
                for row in index_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database stats error: {str(e)}")

@router.get("/logs")
async def get_recent_logs(
    lines: int = 100,
    current_user: UserResponse = Depends(get_current_admin)
):
    """Получение последних логов приложения"""
    try:
        import subprocess
        
        # Чтение последних строк из лог-файла
        result = subprocess.run(
            ['tail', '-n', str(lines), '/var/log/ctf-arena/ctf-arena.log'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
            return {
                "logs": logs,
                "total_lines": len(logs)
            }
        else:
            return {"logs": [], "error": "Failed to read log file"}
            
    except Exception as e:
        return {"logs": [], "error": str(e)}
