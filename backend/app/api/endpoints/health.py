"""
PROJECT THEMIS - Health Endpoint
Version: 5.0
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


def _db_status() -> str:
    try:
        from app.database.connection import engine
        with engine.connect() as _:
            return "connected"
    except Exception:
        return "disconnected"


def _yolo_status() -> str:
    try:
        import main
        return "loaded" if (main.yolo_engine and main.yolo_engine.is_loaded) else "unavailable"
    except Exception:
        return "unavailable"


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns system status and uptime.
    """
    summary = state_manager.get_system_summary()
    yolo_loaded = _yolo_status() == "loaded"
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "5.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": summary["uptimeSeconds"],
            "services": {
                "backend": "running",
                "database": _db_status(),
                "ai": "loaded" if yolo_loaded else "unavailable",
                "websocket": "active",
            },
        },
    }
