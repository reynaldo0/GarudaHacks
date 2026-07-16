"""
PROJECT THEMIS - Recommendation Endpoint
Version: 6.0

Generates redistribution recommendations based on spatial occupancy.
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.core.state_manager import state_manager

router = APIRouter()

WOMEN_CARS = {1, 10}
MAX_RECOMMENDATIONS = 3
MIN_OCCUPANCY_SOURCE = 0.5
MIN_IMBALANCE = 0.12
DISTANCE_WEIGHT = 0.15
OCCUPANCY_WEIGHT = 0.55
BALANCE_WEIGHT = 0.30


def _score_car(car: Any, source_car: Any, cars: list, congestion_avg: float) -> float:
    """Score a destination car (higher = better recommendation)."""
    occ = getattr(car, 'occupancy_ratio', 0)
    distance = abs(car.car_id - source_car.car_id)
    walking_cost = distance * 0.5

    occupancy_score = max(0, 1.0 - occ) * OCCUPANCY_WEIGHT

    balance_score = 0
    if occ < congestion_avg - 0.1:
        balance_score = 0.2 * BALANCE_WEIGHT
    elif occ < congestion_avg:
        balance_score = 0.1 * BALANCE_WEIGHT

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

    sorted_by_occ = sorted(cars, key=lambda c: getattr(c, 'occupancy_ratio', 0), reverse=True)
    source_car = sorted_by_occ[0]

    if getattr(source_car, 'occupancy_ratio', 0) < MIN_OCCUPANCY_SOURCE:
        return {"success": True, "data": None}

    all_occ = [getattr(c, 'occupancy_ratio', 0) for c in cars]
    congestion_avg = sum(all_occ) / len(all_occ) if all_occ else 0
    highest_occ = all_occ[0] if all_occ else 0

    scored = []
    for car in cars:
        if car.car_id == source_car.car_id:
            continue
        diff = getattr(source_car, 'occupancy_ratio', 0) - getattr(car, 'occupancy_ratio', 0)
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
        confidence = min(0.97, score / 1.0 + 0.3)
        is_women = car.car_id in WOMEN_CARS

        label = (
            "#1 Best Choice" if rank == 1 else
            f"#{rank} Alternative"
        )

        recommendations.append({
            "action": "REDISTRIBUTION",
            "fromCarId": source_car.car_id,
            "toCarId": car.car_id,
            "confidence": round(confidence, 2),
            "reason": (
                f"Gerbong {source_car.car_id} {getattr(source_car, 'occupancy_ratio', 0):.0%} -> "
                f"Gerbong {car.car_id} {getattr(car, 'occupancy_ratio', 0):.0%}."
                + (" (Khusus Wanita)" if is_women else "")
            ),
            "priority": rank,
            "label": label,
            "isWomenPriority": is_women,
            "score": round(score, 4),
        })

    return {
        "success": True,
        "data": {
            "fromCarId": source_car.car_id,
            "fromOccupancy": getattr(source_car, 'occupancy_ratio', 0),
            "congestionAvg": round(congestion_avg, 4),
            "highestOccupancy": round(highest_occ, 4),
            "recommendedCars": [r["toCarId"] for r in recommendations],
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
