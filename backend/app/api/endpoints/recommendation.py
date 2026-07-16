"""
PROJECT THEMIS - Recommendation Endpoint
Version: 5.0

This endpoint provides AI-generated recommendations.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/recommendation")
async def get_recommendation():
    """
    Get current AI recommendation.
    Returns the latest recommendation from the Decision Engine.
    """
    trains = state_manager.get_all_trains()
    if not trains:
        return {
            "success": True,
            "data": None,
        }

    train = trains[0]
    cars = train.cars

    # Find the most crowded car and the least crowded car
    if not cars:
        return {
            "success": True,
            "data": None,
        }

    sorted_by_occupancy = sorted(cars, key=lambda c: c.occupancy_percentage, reverse=True)
    most_crowded = sorted_by_occupancy[0]
    least_crowded = sorted_by_occupancy[-1]

    # Only generate recommendation if there's a significant imbalance
    if most_crowded.occupancy_percentage - least_crowded.occupancy_percentage > 20:
        confidence = min(0.95, (most_crowded.occupancy_percentage - least_crowded.occupancy_percentage) / 100)
        return {
            "success": True,
            "data": {
                "action": "MOVE_PASSENGERS",
                "fromCarId": most_crowded.car_id,
                "toCarId": least_crowded.car_id,
                "confidence": round(confidence, 2),
                "reason": f"Car {most_crowded.car_id} is at {most_crowded.occupancy_percentage:.0f}% capacity. "
                         f"Car {least_crowded.car_id} has available space at {least_crowded.occupancy_percentage:.0f}%.",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    return {
        "success": True,
        "data": None,
    }
