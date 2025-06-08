from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from mcp.core.websocket_manager import WebSocketManager

router = APIRouter()
ws_manager = WebSocketManager()

@router.websocket('/ws/notifications')
async def websocket_endpoint(websocket: WebSocket, user_id: str = Query(...)):
    """
    WebSocket endpoint for real-time notifications.
    """
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or handle incoming messages if needed
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket) 