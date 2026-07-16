from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    summary = state_manager.get_system_summary()
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "5.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": summary["uptime_seconds"],
            "services": {
                "backend": "running",
                "database": "connected",
                "ai": "loaded",
                "websocket": "active",
            },
        },
    }
