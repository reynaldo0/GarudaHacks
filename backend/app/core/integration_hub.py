"""
PROJECT THEMIS - Integration Hub
Version: 6.0

Central distribution layer that broadcasts PipelineState to all clients.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional


class IntegrationHub:
    """
    Integration Hub distributes PipelineState to all clients.

    Flow:
    State Manager → Integration Hub → REST API + WebSocket

    Responsibilities:
    - Broadcast pipeline state updates (main V6 event)
    - Broadcast warning updates
    - Broadcast camera status updates
    - Broadcast simulation reset
    - Broadcast system health updates
    """

    def __init__(self):
        self._websocket_manager = None
        self._event_log = []

    def set_websocket_manager(self, manager):
        """Set the WebSocket connection manager."""
        self._websocket_manager = manager

    async def broadcast(self, event_type: str, data: Dict[str, Any], train_id: str = "SF6-001"):
        """Broadcast event to all connected WebSocket clients."""
        message = {
            "type": event_type,
            "train_id": train_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Log event
        self._event_log.append(message)
        if len(self._event_log) > 100:
            self._event_log = self._event_log[-100:]

        # Broadcast via WebSocket
        if self._websocket_manager:
            try:
                await self._websocket_manager.broadcast(message)
            except Exception as e:
                print(f"[IntegrationHub] Broadcast error: {e}")

    async def broadcast_pipeline_state_updated(self, pipeline_state: Dict[str, Any], train_id: str = "SF6-001"):
        """Broadcast pipeline state update (main V6 event)."""
        await self.broadcast("pipeline_state_updated", pipeline_state, train_id)

    async def broadcast_warning_updated(self, warning: Dict[str, Any], train_id: str = "SF6-001"):
        """Broadcast warning update event."""
        await self.broadcast("warning_updated", {
            "warning": warning,
        }, train_id)

    async def broadcast_camera_status_updated(self, camera_id: str, status: str, train_id: str = "SF6-001"):
        """Broadcast camera status update event."""
        await self.broadcast("camera_status_updated", {
            "camera_id": camera_id,
            "status": status,
        }, train_id)

    async def broadcast_simulation_reset(self, message: str = "Simulation reset", train_id: str = "SF6-001"):
        """Broadcast simulation reset event."""
        await self.broadcast("simulation_reset", {
            "message": message,
        }, train_id)

    async def broadcast_system_health_updated(self, health: Dict[str, Any], train_id: str = "SF6-001"):
        """Broadcast system health update event."""
        await self.broadcast("system_health_updated", {
            "health": health,
        }, train_id)

    def get_event_log(self):
        """Get recent event log."""
        return self._event_log


# Global Integration Hub instance
integration_hub = IntegrationHub()
