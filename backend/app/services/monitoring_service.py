import socket
import requests
import time
from sqlalchemy.orm import Session
from app.models.service import Service

class MonitoringService:
    def __init__(self, db: Session):
        self.db = db

    def check_service_status(self, service: Service) -> str:
        """Проверка статуса сервиса"""
        start_time = time.time()
        
        try:
            if service.type == "web":
                status = self._check_http_service(service)
            elif service.type == "ssh":
                status = self._check_ssh_service(service)
            elif service.type == "database":
                status = self._check_database_service(service)
            else:
                status = "unknown"
        except Exception as e:
            status = "offline"
            service.error_message = str(e)

        # Обновляем время ответа
        service.response_time = int((time.time() - start_time) * 1000)
        service.last_checked = time.time()
        service.status = status
        
        self.db.commit()
        
        return status

    def _check_http_service(self, service: Service) -> str:
        """Проверка HTTP сервиса"""
        url = f"http://{service.host}:{service.port}"
        if service.check_endpoint:
            url += service.check_endpoint
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == service.expected_status:
                return "online"
            else:
                return "offline"
        except:
            return "offline"

    def _check_ssh_service(self, service: Service) -> str:
        """Проверка SSH сервиса"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((service.host, service.port))
            sock.close()
            return "online" if result == 0 else "offline"
        except:
            return "offline"

    def _check_database_service(self, service: Service) -> str:
        """Проверка сервиса базы данных"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((service.host, service.port))
            sock.close()
            return "online" if result == 0 else "offline"
        except:
            return "offline"

    def check_all_services(self):
        """Проверка всех сервисов"""
        services = self.db.query(Service).filter(Service.is_active == True).all()
        results = []
        
        for service in services:
            status = self.check_service_status(service)
            results.append({
                "service": service.name,
                "status": status,
                "response_time": service.response_time
            })
        
        return results