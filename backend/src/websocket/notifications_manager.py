import json

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from schemas.notification_schema import NotificationResponse


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def push(self, data: NotificationResponse, user_id: int):
        if user_id not in self.active_connections:
            return
        disconnect = []
        for connection in self.active_connections[user_id]:
            try:
                payload = {
                    "event": "notification",
                    "payload": data.model_dump(mode="json"),
                }
                await connection.send_text(json.dumps(payload))
            except (WebSocketException, WebSocketDisconnect, RuntimeError):
                disconnect.append(connection)
        for conn in disconnect:
            await self.disconnect(user_id, conn)


ws_manager_notifications = ConnectionManager()
