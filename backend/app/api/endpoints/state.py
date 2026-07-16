"""
PROJECT THEMIS - State Endpoint
Version: 6.0

This endpoint provides current system state with PipelineState.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/state")
async def get_state():
    """
    Get current system state.
    Returns complete PipelineState from State Manager.
    """
    trains = state_manager.get_all_trains()
    warnings = state_manager.get_active_warnings()
    summary = state_manager.get_system_summary()

    train_data = None
    if trains:
        train = trains[0]

        # Calculate total occupancy
        total_occupancy = sum(getattr(c, 'occupancy_ratio', 0) for c in train.cars)
        avg_occupancy = total_occupancy / len(train.cars) if train.cars else 0

        # Count density indicators
        green_count = sum(1 for c in train.cars if getattr(c, 'density_indicator', 'GREEN') == 'GREEN')
        yellow_count = sum(1 for c in train.cars if getattr(c, 'density_indicator', 'GREEN') == 'YELLOW')
        red_count = sum(1 for c in train.cars if getattr(c, 'density_indicator', 'GREEN') == 'RED')

        train_data = {
            "id": train.train_id,
            "formation": train.formation,
            "totalCars": train.total_cars,
            "avgOccupancyRatio": round(avg_occupancy, 4),
            "greenCars": green_count,
            "yellowCars": yellow_count,
            "redCars": red_count,
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
                "totalCars": 10,
            },
            "occupancy": train_data or {
                "avgOccupancyRatio": 0,
                "greenCars": 0,
                "yellowCars": 0,
                "redCars": 0,
            },
            "warning": warning_data,
            "system": summary,
        },
    }
