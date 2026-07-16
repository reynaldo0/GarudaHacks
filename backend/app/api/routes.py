from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.state import state_manager

router = APIRouter()


@router.get("/frame")
async def get_frame():
    return {"message": "Frame endpoint"}


@router.post("/frame")
async def receive_frame():
    return {"message": "Frame received"}


@router.get("/state")
async def get_state():
    return state_manager.get_state()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "update", "data": data})
    except WebSocketDisconnect:
        print("Client disconnected")
