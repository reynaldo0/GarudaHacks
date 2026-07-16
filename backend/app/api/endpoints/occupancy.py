"""
PROJECT THEMIS - Occupancy Endpoint
Version: 5.0

This endpoint provides occupancy information.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/occupancy")
async def get_occupancy():
    """
    Get current occupancy status.
    Returns occupancy for all cars in the current train.
    """
    trains = state_manager.get_all_trains()
    if not trains:
        return {
            "success": True,
            "data": {
                "trainId": "SF10",
                "station": "Manggarai",
                "timestamp": datetime.utcnow().isoformat(),
                "cars": [],
            },
        }

    train = trains[0]
    return {
        "success": True,
        "data": {
            "trainId": train.train_id,
            "station": "Manggarai",
            "timestamp": train.timestamp.isoformat(),
            "cars": [
                {
                    "carId": car.car_id,
                    "occupancyPct": car.occupancy_percentage,
                    "status": car.status,
                    "passengers": car.detected_persons,
                    "capacity": car.capacity,
                    "cameraStatus": "active" if car.camera_id else "inactive",
                    "cameraId": car.camera_id,
                    "riskScore": car.risk_score,
                }
                for car in train.cars
            ],
        },
    }


@router.get("/occupancy/{car_id}")
async def get_car_occupancy(car_id: int):
    """Get occupancy for specific car."""
    trains = state_manager.get_all_trains()
    for train in trains:
        for car in train.cars:
            if car.car_id == car_id:
                return {
                    "success": True,
                    "data": {
                        "carId": car.car_id,
                        "occupancyPct": car.occupancy_percentage,
                        "status": car.status,
                        "passengers": car.detected_persons,
                        "capacity": car.capacity,
                        "riskScore": car.risk_score,
                        "timestamp": car.timestamp.isoformat(),
                    },
                }
    return {
        "success": False,
        "data": {"message": f"Car {car_id} not found"},
    }
