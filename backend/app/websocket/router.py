"""
PROJECT THEMIS - WebSocket Router
Version: 5.0

This module handles WebSocket connections for real-time updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any

ws_router = APIRouter()


class ConnectionManager:
    """
    WebSocket Connection Manager.
    Manages all connected WebSocket clients.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        snapshot = list(self.active_connections)
        disconnected = []
        for connection in snapshot:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Global connection manager
manager = ConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Clients receive: OccupancyUpdated, WarningUpdated, RecommendationChanged
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Echo back or handle specific messages
            print(f"[WS] Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)


# Export manager for use in other modules
__all__ = ["ws_router", "manager"]
