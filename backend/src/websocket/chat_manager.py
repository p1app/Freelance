import json

from fastapi import WebSocket, WebSocketException
from schemas.chat_schema import MessageResponse


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, contract_id: int, websocket: WebSocket):
        await websocket.accept()
        if contract_id not in self.active_connections:
            self.active_connections[contract_id] = []
        self.active_connections[contract_id].append(websocket)

    async def disconnect(self, contract_id: int, websocket: WebSocket):
        if contract_id in self.active_connections:
            if websocket in self.active_connections[contract_id]:
                self.active_connections[contract_id].remove(websocket)
            if not self.active_connections[contract_id]:
                del self.active_connections[contract_id]

    async def broadcast(self, message: MessageResponse, contract_id: int):
        if contract_id not in self.active_connections:
            return
        disconnect = []
        for connection in self.active_connections[contract_id]:
            try:
                payload = {"type": "new_message", **message.model_dump(mode="json")}
                await connection.send_text(json.dumps(payload, default=str))
            except WebSocketException:
                disconnect.append(connection)
        for conn in disconnect:
            await self.disconnect(contract_id, conn)


ws_manager_chat = ConnectionManager()
