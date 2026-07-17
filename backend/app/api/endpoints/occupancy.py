"""
PROJECT THEMIS - Occupancy Endpoint
Version: 6.0

This endpoint provides spatial occupancy information.
"""

import random
from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


def _generate_prediction(car_id: int, occupancy_ratio: float) -> dict:
    """Generate a prediction on-the-fly based current spatial occupancy."""
    rng = random.Random(car_id + int(datetime.utcnow().timestamp()) // 60)

    if occupancy_ratio < 0.3:
        trend = "stable"
        predicted = occupancy_ratio + rng.uniform(-0.02, 0.05)
        confidence = 0.90
    elif occupancy_ratio < 0.6:
        delta = rng.uniform(-0.03, 0.06)
        predicted = occupancy_ratio + delta
        trend = "increasing" if delta > 0.02 else "decreasing" if delta < -0.02 else "stable"
        confidence = round(rng.uniform(0.72, 0.85), 2)
    elif occupancy_ratio < 0.8:
        delta = rng.uniform(-0.02, 0.08)
        predicted = occupancy_ratio + delta
        trend = "increasing" if delta > 0.03 else "decreasing" if delta < -0.01 else "stable"
        confidence = round(rng.uniform(0.70, 0.88), 2)
    else:
        delta = rng.uniform(0.01, 0.10)
        predicted = occupancy_ratio + delta
        trend = "increasing"
        confidence = round(rng.uniform(0.80, 0.92), 2)

    predicted = max(0.0, min(1.0, predicted))

    return {
        "trend": trend,
        "predictedOccupancyRatio": round(predicted, 4),
        "confidence": confidence,
        "horizonMinutes": 15,
    }


@router.get("/occupancy")
async def get_occupancy():
    """
    Get current spatial occupancy status with predictions.
    Returns occupancy for all cars in the current train.
    """
    trains = state_manager.get_all_trains()
    if not trains:
        return {
            "success": True,
            "data": {
                "trainId": "SF6",
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
                    "occupancyRatio": getattr(car, 'occupancy_ratio', 0),
                    "freeSpaceRatio": getattr(car, 'free_space_ratio', 1),
                    "densityIndicator": getattr(car, 'density_indicator', 'GREEN'),
                    "spatialOccupancyScore": getattr(car, 'spatial_occupancy_score', 0),
                    "cameraStatus": "active" if car.camera_id else "inactive",
                    "cameraId": car.camera_id,
                    "riskScore": car.risk_score,
                    "prediction": _generate_prediction(car.car_id, getattr(car, 'occupancy_ratio', 0)),
                }
                for car in train.cars
            ],
        },
    }


@router.get("/occupancy/{car_id}")
async def get_car_occupancy(car_id: int):
    """Get spatial occupancy for specific car with prediction."""
    trains = state_manager.get_all_trains()
    for train in trains:
        for car in train.cars:
            if car.car_id == car_id:
                return {
                    "success": True,
                    "data": {
                        "carId": car.car_id,
                        "occupancyRatio": getattr(car, 'occupancy_ratio', 0),
                        "freeSpaceRatio": getattr(car, 'free_space_ratio', 1),
                        "densityIndicator": getattr(car, 'density_indicator', 'GREEN'),
                        "spatialOccupancyScore": getattr(car, 'spatial_occupancy_score', 0),
                        "riskScore": car.risk_score,
                        "cameraStatus": "active" if car.camera_id else "inactive",
                        "cameraId": car.camera_id,
                        "prediction": _generate_prediction(car.car_id, getattr(car, 'occupancy_ratio', 0)),
                        "timestamp": car.timestamp.isoformat(),
                    },
                }
    return {
        "success": False,
        "data": {"message": f"Car {car_id} not found"},
    }
