"""
PROJECT THEMIS - Recommendation Endpoint
Version: 7.0

Generates ranked multi-destination AI recommendations.
Returns a list of recommended destination cars ranked by score.
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.core.state_manager import state_manager

router = APIRouter()

WOMEN_CARS = {1, 10}
MAX_RECOMMENDATIONS = 3
MIN_OCCUPANCY_SOURCE = 50
MIN_IMBALANCE = 12
DISTANCE_WEIGHT = 0.15
OCCUPANCY_WEIGHT = 0.55
BALANCE_WEIGHT = 0.30


def _score_car(car: Any, source_car: Any, cars: list, congestion_avg: float) -> float:
    """Score a destination car (higher = better recommendation)."""
    occ = car.occupancy_percentage
    distance = abs(car.car_id - source_car.car_id)
    walking_cost = distance * 0.5

    occupancy_score = max(0, 100 - occ) * OCCUPANCY_WEIGHT

    balance_score = 0
    if occ < congestion_avg - 10:
        balance_score = 20 * BALANCE_WEIGHT
    elif occ < congestion_avg:
        balance_score = 10 * BALANCE_WEIGHT

    distance_penalty = walking_cost * DISTANCE_WEIGHT

    return occupancy_score + balance_score - distance_penalty


@router.get("/recommendation")
async def get_recommendation():
    trains = state_manager.get_all_trains()
    if not trains:
        return {"success": True, "data": None}

    train = trains[0]
    cars = train.cars

    if not cars:
        return {"success": True, "data": None}

    sorted_by_occ = sorted(cars, key=lambda c: c.occupancy_percentage, reverse=True)
    source_car = sorted_by_occ[0]

    if source_car.occupancy_percentage < MIN_OCCUPANCY_SOURCE:
        return {"success": True, "data": None}

    all_occ = [c.occupancy_percentage for c in cars]
    congestion_avg = sum(all_occ) / len(all_occ) if all_occ else 0
    highest_occ = all_occ[0] if all_occ else 0

    scored = []
    for car in cars:
        if car.car_id == source_car.car_id:
            continue
        diff = source_car.occupancy_percentage - car.occupancy_percentage
        if diff < MIN_IMBALANCE:
            continue
        score = _score_car(car, source_car, cars, congestion_avg)
        scored.append((score, car))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return {"success": True, "data": None}

    top = scored[:MAX_RECOMMENDATIONS]

    recommendations = []
    for rank, (score, car) in enumerate(top, 1):
        confidence = min(0.97, score / 100 + 0.3)
        passengers_estimate = max(3, int(
            (source_car.occupancy_percentage - car.occupancy_percentage) * 1.5
        ))
        is_women = car.car_id in WOMEN_CARS

        label = (
            "#1 Best Choice" if rank == 1 else
            f"#{rank} Alternative"
        )

        recommendations.append({
            "action": "MOVE_PASSENGERS",
            "fromCarId": source_car.car_id,
            "toCarId": car.car_id,
            "confidence": round(confidence, 2),
            "reason": (
                f"Gerbong {source_car.car_id} {source_car.occupancy_percentage:.0f}% -> "
                f"Gerbong {car.car_id} {car.occupancy_percentage:.0f}%."
                + (" (Khusus Wanita)" if is_women else "")
            ),
            "priority": rank,
            "label": label,
            "isWomenPriority": is_women,
            "passengersToMove": passengers_estimate,
            "score": round(score, 1),
        })

    return {
        "success": True,
        "data": {
            "fromCarId": source_car.car_id,
            "fromOccupancy": source_car.occupancy_percentage,
            "congestionAvg": round(congestion_avg, 1),
            "highestOccupancy": round(highest_occ, 1),
            "recommendedCars": [r["toCarId"] for r in recommendations],
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
