# backend/app/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Any  # Добавьте Any здесь
import json
import uuid
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, Set[str]] = defaultdict(set)
        self.team_connections: Dict[int, Set[str]] = defaultdict(set)
        self.connection_info: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: int, team_id: int, username: str):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id].add(connection_id)
        self.team_connections[team_id].add(connection_id)
        self.connection_info[connection_id] = {
            "user_id": user_id,
            "team_id": team_id,
            "username": username
        }
        
        # Уведомляем команду о новом подключении
        await self.broadcast_to_team(
            team_id,
            {
                "type": "user_connected",
                "user_id": user_id,
                "username": username,
                "connection_count": len(self.team_connections[team_id]),
                "timestamp": self._get_timestamp()
            }
        )
        
        print(f"🔗 WebSocket connected: {username} (team {team_id})")

    async def disconnect(self, connection_id: str):
        if connection_id in self.connection_info:
            info = self.connection_info[connection_id]
            user_id = info["user_id"]
            team_id = info["team_id"]
            username = info["username"]
            
            # Удаляем соединение из всех коллекций
            self.user_connections[user_id].discard(connection_id)
            self.team_connections[team_id].discard(connection_id)
            del self.connection_info[connection_id]
            del self.active_connections[connection_id]
            
            # Уведомляем команду об отключении
            await self.broadcast_to_team(
                team_id,
                {
                    "type": "user_disconnected",
                    "user_id": user_id,
                    "username": username,
                    "connection_count": len(self.team_connections[team_id]),
                    "timestamp": self._get_timestamp()
                }
            )
            
            print(f"🔌 WebSocket disconnected: {username}")

    async def send_personal_message(self, user_id: int, message: dict):
        """Отправка сообщения конкретному пользователю"""
        if user_id in self.user_connections:
            disconnected = set()
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_json(message)
                    except:
                        disconnected.add(connection_id)
            
            # Очищаем отключенные соединения
            for connection_id in disconnected:
                await self.disconnect(connection_id)

    async def broadcast_to_team(self, team_id: int, message: dict):
        """Трансляция сообщения всей команде"""
        if team_id in self.team_connections:
            disconnected = set()
            for connection_id in self.team_connections[team_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_json(message)
                    except:
                        disconnected.add(connection_id)
            
            # Очищаем отключенные соединения
            for connection_id in disconnected:
                await self.disconnect(connection_id)

    async def broadcast_to_all(self, message: dict):
        """Трансляция сообщения всем подключенным клиентам"""
        disconnected = set()
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(connection_id)
        
        # Очищаем отключенные соединения
        for connection_id in disconnected:
            await self.disconnect(connection_id)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Статистика подключений"""
        return {
            "total_connections": len(self.active_connections),
            "users_connected": len(self.user_connections),
            "teams_connected": len(self.team_connections),
            "connections_per_team": {
                team_id: len(connections) 
                for team_id, connections in self.team_connections.items()
            }
        }

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Глобальный экземпляр менеджера
manager = ConnectionManager()

# WebSocket endpoint
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user_ws

router = APIRouter()

@router.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket, user_data: dict = Depends(get_current_user_ws)):
    """WebSocket endpoint для арены CTF"""
    user_id = user_data["user_id"]
    team_id = user_data["team_id"]
    username = user_data["username"]
    
    await manager.connect(websocket, user_id, team_id, username)
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_arena_message(websocket, data, user_data)
    except WebSocketDisconnect:
        # ConnectionManager автоматически обработает отключение
        pass

async def handle_arena_message(websocket: WebSocket, data: dict, user_data: dict):
    """Обработка входящих WebSocket сообщений"""
    message_type = data.get("type")
    user_id = user_data["user_id"]
    team_id = user_data["team_id"]
    username = user_data["username"]
    
    if message_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": manager._get_timestamp()
        })
    
    elif message_type == "flag_submission":
        # Обработка отправки флага через WebSocket
        await handle_flag_submission(data, user_data)
    
    elif message_type == "get_team_status":
        # Отправка статуса команды
        await send_team_status(team_id, user_id)
    
    elif message_type == "chat_message":
        # Чат команды
        await manager.broadcast_to_team(team_id, {
            "type": "chat_message",
            "user_id": user_id,
            "username": username,
            "message": data["message"],
            "timestamp": manager._get_timestamp()
        })

async def handle_flag_submission(data: dict, user_data: dict):
    """Обработка отправки флага через WebSocket"""
    from app.services.flag_service import FlagService
    from app.core.database import get_db
    from sqlalchemy.orm import Session
    import asyncio
    
    # Запускаем в отдельном потоке чтобы не блокировать WebSocket
    def sync_submit_flag():
        with next(get_db()) as db:
            flag_service = FlagService(db)
            # Здесь логика проверки флага...
            return {"status": "accepted", "points": 100}
    
    result = await asyncio.get_event_loop().run_in_executor(None, sync_submit_flag)
    
    # Отправляем результат пользователю
    await manager.send_personal_message(user_data["user_id"], {
        "type": "flag_result",
        "challenge_id": data["challenge_id"],
        "result": result,
        "timestamp": manager._get_timestamp()
    })
    
    # Уведомляем команду о успешной отправке
    if result["status"] == "accepted":
        await manager.broadcast_to_team(user_data["team_id"], {
            "type": "team_flag_submitted",
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "challenge_id": data["challenge_id"],
            "points": result["points"],
            "timestamp": manager._get_timestamp()
        })

async def send_team_status(team_id: int, user_id: int):
    """Отправка текущего статуса команды"""
    from app.services.team_service import TeamService
    from app.core.database import get_db
    
    with next(get_db()) as db:
        team_service = TeamService(db)
        status = team_service.get_team_status(team_id)
        
        await manager.send_personal_message(user_id, {
            "type": "team_status",
            "status": status,
            "timestamp": manager._get_timestamp()
        })
