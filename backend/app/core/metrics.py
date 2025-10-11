# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Метрики приложения
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Total active users'
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_connections_total',
    'Total WebSocket connections'
)

SUBMISSION_COUNT = Counter(
    'flag_submissions_total',
    'Total flag submissions',
    ['status']
)

def metrics_endpoint():
    """Endpoint для Prometheus метрик"""
    return Response(generate_latest(), media_type="text/plain")