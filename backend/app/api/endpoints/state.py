from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/state")
async def get_state():
    """
    Get current system state.
    Returns complete state from State Manager.
    """
    trains = state_manager.get_all_trains()
    warnings = state_manager.get_active_warnings()
    summary = state_manager.get_system_summary()

    train_data = None
    if trains:
        train = trains[0]
        total_passengers = sum(c.detected_persons for c in train.cars)
        total_capacity = sum(c.capacity for c in train.cars)
        pct = (total_passengers / total_capacity * 100) if total_capacity > 0 else 0

        train_data = {
            "id": train.train_id,
            "formation": train.formation,
            "capacity": 200,
            "total_cars": train.total_cars,
            "total_passengers": total_passengers,
            "total_capacity": total_capacity,
            "percentage": round(pct, 2),
            "status": state_manager._calculate_status(pct),
        }

    warning_data = None
    if warnings:
        w = warnings[-1]
        warning_data = {
            "active": True,
            "type": w.warning_type,
            "severity": w.severity,
            "car_id": w.car_id,
            "message": w.message,
        }

    return {
        "success": True,
        "data": {
            "timestamp": datetime.utcnow().isoformat(),
            "station": {"id": "manggarai", "name": "Manggarai Station"},
            "train": train_data or {
                "id": "SF10",
                "formation": "SF10",
                "capacity": 200,
                "total_cars": 10,
            },
            "occupancy": train_data or {
                "total_passengers": 0,
                "total_capacity": 2000,
                "percentage": 0,
                "status": "UNKNOWN",
            },
            "warning": warning_data,
            "system": summary,
        },
    }
