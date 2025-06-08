"""
WebSocket manager for real-time user updates and notifications.
"""
from typing import Dict, Set, Any
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        # Track user_id to set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: Any):
        for ws in self.active_connections.get(user_id, set()):
            await ws.send_json(message)

    async def broadcast(self, message: Any):
        for user_ws_set in self.active_connections.values():
            for ws in user_ws_set:
                await ws.send_json(message) 