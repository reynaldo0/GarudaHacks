"""
PROJECT THEMIS - State Endpoint
Version: 5.0

This endpoint provides current system state.
"""

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
            "totalCars": train.total_cars,
            "totalPassengers": total_passengers,
            "totalCapacity": total_capacity,
            "percentage": round(pct, 2),
            "status": state_manager._calculate_status(pct),
        }

    warning_data = None
    if warnings:
        w = warnings[-1]
        warning_data = {
            "id": f"{w.train_id}-{w.car_id}-{w.warning_type}",
            "isActive": True,
            "warningType": w.warning_type,
            "severity": w.severity,
            "carId": w.car_id,
            "trainId": w.train_id,
            "message": w.message,
            "timestamp": w.timestamp.isoformat() if w.timestamp else datetime.utcnow().isoformat(),
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
                "totalPassengers": 0,
                "totalCapacity": 2000,
                "percentage": 0,
                "status": "UNKNOWN",
            },
            "warning": warning_data,
            "system": summary,
        },
    }
