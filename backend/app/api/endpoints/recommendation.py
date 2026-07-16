"""
PROJECT THEMIS - Recommendation Endpoint
Version: 6.0

Generates AI recommendations with women-priority car logic.
Cars 1 & 10 are designated women-priority cars (secondary recommendation).
Primary recommendations target general cars (2-9).
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.core.state_manager import state_manager

router = APIRouter()

WOMEN_PRIORITY_CARS = {1, 10}
GENERAL_CARS_RANGE = (2, 9)
IMBALANCE_THRESHOLD = 15


def _is_women_car(car_id: int) -> bool:
    return car_id in WOMEN_PRIORITY_CARS


def _build_recommendation(
    from_car_id: int,
    to_car_id: int,
    from_occ: float,
    to_occ: float,
    confidence: float,
    reason: str,
    priority: int = 1,
    passengers_to_move: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "action": "MOVE_PASSENGERS",
        "fromCarId": from_car_id,
        "toCarId": to_car_id,
        "confidence": round(confidence, 2),
        "reason": reason,
        "priority": priority,
        "isWomenPriority": _is_women_car(to_car_id),
        "passengersToMove": passengers_to_move,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _find_best_target(
    cars: list,
    source_car_id: int,
    exclude_ids: set,
) -> Optional[Dict[str, Any]]:
    """Find the best target car from general (non-women) cars first."""
    candidates = [
        c for c in cars
        if c.car_id != source_car_id
        and c.car_id not in exclude_ids
        and c.car_id not in WOMEN_PRIORITY_CARS
        and GENERAL_CARS_RANGE[0] <= c.car_id <= GENERAL_CARS_RANGE[1]
    ]

    if not candidates:
        return None

    candidates.sort(key=lambda c: c.occupancy_percentage)
    best = candidates[0]
    return {
        "car_id": best.car_id,
        "occupancy": best.occupancy_percentage,
    }


def _find_women_target(
    cars: list,
    source_car_id: int,
) -> Optional[Dict[str, Any]]:
    """Find the best women-priority target (car 1 or 10) if it's among the lowest."""
    women_candidates = [
        c for c in cars
        if c.car_id in WOMEN_PRIORITY_CARS
        and c.car_id != source_car_id
    ]

    if not women_candidates:
        return None

    women_candidates.sort(key=lambda c: c.occupancy_percentage)
    best_women = women_candidates[0]

    general_candidates = [
        c for c in cars
        if c.car_id not in WOMEN_PRIORITY_CARS
        and c.car_id != source_car_id
    ]

    if not general_candidates:
        return {
            "car_id": best_women.car_id,
            "occupancy": best_women.occupancy_percentage,
        }

    general_avg = sum(c.occupancy_percentage for c in general_candidates) / len(general_candidates)

    if best_women.occupancy_percentage < general_avg - 5:
        return {
            "car_id": best_women.car_id,
            "occupancy": best_women.occupancy_percentage,
        }

    return None


@router.get("/recommendation")
async def get_recommendation():
    """
    Get current AI recommendation with women-priority car logic.

    Priority 1: Move passengers to general car (2-9) with lowest occupancy
    Priority 2: If women cars (1/10) have significantly lower occupancy,
                also recommend them as secondary option
    """
    trains = state_manager.get_all_trains()
    if not trains:
        return {"success": True, "data": None}

    train = trains[0]
    cars = train.cars

    if not cars:
        return {"success": True, "data": None}

    sorted_by_occ = sorted(cars, key=lambda c: c.occupancy_percentage, reverse=True)
    most_crowded = sorted_by_occ[0]

    if most_crowded.occupancy_percentage < 50:
        return {"success": True, "data": None}

    primary_target = _find_best_target(cars, most_crowded.car_id, set())

    if primary_target is None:
        return {"success": True, "data": None}

    primary_diff = most_crowded.occupancy_percentage - primary_target["occupancy"]

    if primary_diff < IMBALANCE_THRESHOLD:
        return {"success": True, "data": None}

    confidence = min(0.95, primary_diff / 100 + 0.3)
    passengers_estimate = max(5, int(primary_diff * 1.5))

    primary_rec = _build_recommendation(
        from_car_id=most_crowded.car_id,
        to_car_id=primary_target["car_id"],
        from_occ=most_crowded.occupancy_percentage,
        to_occ=primary_target["occupancy"],
        confidence=confidence,
        reason=(
            f"Gerbong {most_crowded.car_id} mencapai {most_crowded.occupancy_percentage:.0f}% kapasitas. "
            f"Gerbong {primary_target['car_id']} memiliki ruang tersedia di {primary_target['occupancy']:.0f}%."
        ),
        priority=1,
        passengers_to_move=passengers_estimate,
    )

    women_target = _find_women_target(cars, most_crowded.car_id)

    if women_target and women_target["car_id"] != primary_target["car_id"]:
        women_diff = most_crowded.occupancy_percentage - women_target["occupancy"]
        if women_diff > IMBALANCE_THRESHOLD:
            women_confidence = min(0.90, women_diff / 100 + 0.25)
            women_passengers = max(3, int(women_diff * 1.2))

            primary_rec["womenAlternative"] = _build_recommendation(
                from_car_id=most_crowded.car_id,
                to_car_id=women_target["car_id"],
                from_occ=most_crowded.occupancy_percentage,
                to_occ=women_target["occupancy"],
                confidence=women_confidence,
                reason=(
                    f"Gerbong {women_target['car_id']} (Khusus Wanita) hanya {women_target['occupancy']:.0f}% terisi. "
                    f"Prioritas kedua untuk penumpang wanita."
                ),
                priority=2,
                passengers_to_move=women_passengers,
            )

    return {"success": True, "data": primary_rec}
