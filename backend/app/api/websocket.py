from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from typing import List, Dict

websocket_router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect_post(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Gửi số like hiện tại khi mới kết nối
        # await websocket.send_text(f"{self.like_count}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def like(self):
        self.like_count += 1
        await self.broadcast()

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect_post(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "like":
                await manager.like()
    except WebSocketDisconnect:
        manager.disconnect(websocket)