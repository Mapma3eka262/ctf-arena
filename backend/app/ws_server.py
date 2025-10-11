# backend/app/ws_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.api.websocket import manager, websocket_arena
from app.core.config import settings

app = FastAPI(title="CTF WebSocket Server")

# Подключение WebSocket endpoint
app.websocket("/ws/arena")(websocket_arena)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "websocket",
        "connections": manager.get_connection_stats()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.ws_server:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )