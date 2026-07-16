"""
PROJECT THEMIS - Simulation Seeder
Version: 5.0

Comprehensive data seeder with realistic KRL Commuter Line data patterns.
Populates the State Manager with accurate occupancy, predictions, warnings,
recommendations, camera status, and decisions for the SF10 formation.

Based on real Jakarta KRL commuter train characteristics:
- SF10 = 10-car formation, 200 capacity per car (2000 total)
- Cars 1 & 10 are end cars (near exits) - typically higher occupancy
- Cars 4-7 are middle cars - moderate occupancy
- Peak hours (06:00-09:00, 16:00-19:00): 70-100% occupancy
- Normal hours: 30-60% occupancy
- Off-peak/holiday: 5-25% occupancy
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub

# ─── SF10 Formation Constants ──────────────────────────────────────────────────
TRAIN_ID = "SF10-001"
CAPACITY_PER_CAR = 200
TOTAL_CARS = 10
FORMATION = "SF10"

# Camera IDs: 2 per car (cabin cameras)
CAMERA_IDS = [
    f"car{str(i).zfill(2)}_cam{str(j).zfill(2)}"
    for i in range(1, TOTAL_CARS + 1)
    for j in (1, 2)
]

# ─── Status Thresholds (matching StateManager) ─────────────────────────────────
def _status(pct: float) -> str:
    if pct < 40:
        return "LOW"
    elif pct < 70:
        return "NORMAL"
    elif pct < 90:
        return "HIGH"
    elif pct <= 100:
        return "FULL"
    else:
        return "OVERCAPACITY"


def _risk(pct: float) -> float:
    if pct < 40:
        return 0.1
    elif pct < 70:
        return 0.3
    elif pct < 90:
        return 0.7
    elif pct <= 100:
        return 0.9
    else:
        return 1.0


# ─── Scenario Definitions ──────────────────────────────────────────────────────
# Each scenario defines realistic passenger counts per car based on actual
# KRL commuter patterns. Car 1 and 10 are near platform exits, so they tend
# to have higher occupancy during boarding. Middle cars (4-6) tend to be
# more stable.

SCENARIOS = {
    "empty": {
        "description": "Empty train - no passengers",
        "pattern": "empty",
        "cars": [{"car_id": i, "passengers": 0} for i in range(1, 11)],
    },
    "normal": {
        "description": "Normal operation - balanced mid-day traffic",
        "pattern": "normal",
        "cars": [
            {"car_id": 1, "passengers": 85},   # end car, near exit
            {"car_id": 2, "passengers": 72},
            {"car_id": 3, "passengers": 68},
            {"car_id": 4, "passengers": 75},
            {"car_id": 5, "passengers": 80},   # middle, near doors
            {"car_id": 6, "passengers": 78},
            {"car_id": 7, "passengers": 70},
            {"car_id": 8, "passengers": 65},
            {"car_id": 9, "passengers": 58},
            {"car_id": 10, "passengers": 62},  # end car
        ],
    },
    "peak_hour": {
        "description": "Rush hour congestion - morning/evening peak",
        "pattern": "peak",
        "cars": [
            {"car_id": 1, "passengers": 175},  # end car, exit side - very crowded
            {"car_id": 2, "passengers": 160},
            {"car_id": 3, "passengers": 145},
            {"car_id": 4, "passengers": 155},
            {"car_id": 5, "passengers": 185},  # middle, door-heavy
            {"car_id": 6, "passengers": 195},  # peak of peak
            {"car_id": 7, "passengers": 170},
            {"car_id": 8, "passengers": 140},
            {"car_id": 9, "passengers": 130},
            {"car_id": 10, "passengers": 110}, # far end, less crowded
        ],
    },
    "holiday": {
        "description": "Holiday - light recreational traffic",
        "pattern": "holiday",
        "cars": [
            {"car_id": 1, "passengers": 35},
            {"car_id": 2, "passengers": 28},
            {"car_id": 3, "passengers": 22},
            {"car_id": 4, "passengers": 30},
            {"car_id": 5, "passengers": 40},
            {"car_id": 6, "passengers": 45},
            {"car_id": 7, "passengers": 32},
            {"car_id": 8, "passengers": 25},
            {"car_id": 9, "passengers": 18},
            {"car_id": 10, "passengers": 15},
        ],
    },
    "imbalanced": {
        "description": "Heavy imbalance - test recommendation engine",
        "pattern": "imbalanced",
        "cars": [
            {"car_id": 1, "passengers": 195},  # near overcapacity
            {"car_id": 2, "passengers": 188},  # full
            {"car_id": 3, "passengers": 180},  # high
            {"car_id": 4, "passengers": 95},   # normal
            {"car_id": 5, "passengers": 40},   # low
            {"car_id": 6, "passengers": 30},   # low
            {"car_id": 7, "passengers": 25},   # low
            {"car_id": 8, "passengers": 20},   # low
            {"car_id": 9, "passengers": 15},   # low
            {"car_id": 10, "passengers": 10},  # low
        ],
    },
    "emergency": {
        "description": "Emergency scenario - multiple overcapacity cars",
        "pattern": "emergency",
        "cars": [
            {"car_id": 1, "passengers": 210},  # overcapacity
            {"car_id": 2, "passengers": 205},  # overcapacity
            {"car_id": 3, "passengers": 198},  # near full
            {"car_id": 4, "passengers": 200},  # full
            {"car_id": 5, "passengers": 195},  # near full
            {"car_id": 6, "passengers": 190},  # high
            {"car_id": 7, "passengers": 185},  # high
            {"car_id": 8, "passengers": 180},  # high
            {"car_id": 9, "passengers": 170},  # high
            {"car_id": 10, "passengers": 165}, # high
        ],
    },
}

DEFAULT_SCENARIO = "peak_hour"


# ─── Prediction Generator ──────────────────────────────────────────────────────

def _generate_prediction(car_id: int, current_pct: float, pattern: str) -> Dict:
    """
    Generate a realistic occupancy prediction based on current state and scenario pattern.
    Returns prediction with trend, predictedOccupancy, confidence, and horizon_minutes.
    """
    rng = random.Random(car_id + int(time.time()) % 100)

    if pattern == "empty":
        trend = "stable"
        predicted = 0.0
        confidence = 0.95
    elif pattern == "normal":
        # Slight fluctuation around current
        delta = rng.uniform(-3, 5)
        predicted = max(0, min(100, current_pct + delta))
        if delta > 2:
            trend = "increasing"
        elif delta < -2:
            trend = "decreasing"
        else:
            trend = "stable"
        confidence = round(rng.uniform(0.70, 0.88), 2)
    elif pattern == "peak":
        # Generally increasing as more passengers board
        delta = rng.uniform(1, 8)
        predicted = max(0, min(120, current_pct + delta))
        if current_pct > 85:
            trend = "increasing"  # still getting worse
        elif current_pct > 60:
            trend = "increasing"
        else:
            trend = "stable"
        confidence = round(rng.uniform(0.72, 0.90), 2)
    elif pattern == "holiday":
        # Stable or slightly decreasing
        delta = rng.uniform(-4, 2)
        predicted = max(0, min(60, current_pct + delta))
        trend = "decreasing" if delta < -1 else "stable"
        confidence = round(rng.uniform(0.75, 0.92), 2)
    elif pattern == "imbalanced":
        # Hot cars getting hotter, cold cars staying cold
        if current_pct > 70:
            delta = rng.uniform(2, 6)
            trend = "increasing"
        else:
            delta = rng.uniform(-2, 1)
            trend = "stable" if abs(delta) < 1 else "decreasing"
        predicted = max(0, min(120, current_pct + delta))
        confidence = round(rng.uniform(0.68, 0.85), 2)
    elif pattern == "emergency":
        # All cars trending toward overcapacity
        delta = rng.uniform(2, 10)
        predicted = max(0, min(150, current_pct + delta))
        trend = "increasing"
        confidence = round(rng.uniform(0.80, 0.95), 2)
    else:
        predicted = current_pct
        trend = "stable"
        confidence = 0.5

    return {
        "trend": trend,
        "predictedOccupancy": round(predicted, 2),
        "confidence": confidence,
        "horizon_minutes": 15,
        "riskScore": round(_risk(predicted), 2),
    }


# ─── Recommendation Generator ──────────────────────────────────────────────────

def _generate_recommendation(cars_data: List[Dict]) -> Optional[Dict]:
    """
    Generate a MOVE_PASSENGERS recommendation if significant imbalance exists.
    Matches the logic from recommendation.py endpoint and cales_engine.py.
    """
    if not cars_data:
        return None

    sorted_cars = sorted(cars_data, key=lambda c: c["passengers"], reverse=True)
    most_crowded = sorted_cars[0]
    least_crowded = sorted_cars[-1]

    most_pct = (most_crowded["passengers"] / CAPACITY_PER_CAR) * 100
    least_pct = (least_crowded["passengers"] / CAPACITY_PER_CAR) * 100

    imbalance = most_pct - least_pct

    if imbalance > 20 and most_pct > 50:
        confidence = min(0.95, imbalance / 100)
        move_count = min(
            int((imbalance / 100) * CAPACITY_PER_CAR * 0.3),
            most_crowded["passengers"] - int(CAPACITY_PER_CAR * 0.4),
        )
        move_count = max(5, move_count)

        return {
            "action": "MOVE_PASSENGERS",
            "fromCarId": most_crowded["car_id"],
            "toCarId": least_crowded["car_id"],
            "confidence": round(confidence, 2),
            "reason": (
                f"Car {most_crowded['car_id']} is at {most_pct:.0f}% capacity "
                f"({most_crowded['passengers']}/{CAPACITY_PER_CAR}). "
                f"Car {least_crowded['car_id']} has available space at "
                f"{least_pct:.0f}% ({least_crowded['passengers']}/{CAPACITY_PER_CAR}). "
                f"Move ~{move_count} passengers to balance occupancy."
            ),
            "passengersToMove": move_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    return None


# ─── Warning Generator ─────────────────────────────────────────────────────────

def _generate_warnings(cars_data: List[Dict], train_id: str) -> List[Dict]:
    """
    Generate warnings for cars with HIGH, FULL, or OVERCAPACITY status.
    Matches the logic from state_manager._check_warnings().
    """
    warnings = []
    now = datetime.utcnow()

    for car in cars_data:
        pct = (car["passengers"] / CAPACITY_PER_CAR) * 100
        status = _status(pct)

        if status in ("HIGH", "FULL", "OVERCAPACITY"):
            severity = "CRITICAL" if status in ("FULL", "OVERCAPACITY") else "WARNING"
            warning_type = f"{status}_OCCUPANCY"

            if status == "OVERCAPACITY":
                message = (
                    f"Car {car['car_id']} is OVERCAPACITY at {pct:.0f}% "
                    f"({car['passengers']}/{CAPACITY_PER_CAR} passengers). "
                    f"Immediate passenger redistribution required."
                )
            elif status == "FULL":
                message = (
                    f"Car {car['car_id']} is FULL at {pct:.0f}% "
                    f"({car['car_id']}/{CAPACITY_PER_CAR} passengers). "
                    f"Passengers should move to less crowded cars."
                )
            else:
                message = (
                    f"Car {car['car_id']} is HIGH occupancy at {pct:.0f}% "
                    f"({car['passengers']}/{CAPACITY_PER_CAR} passengers). "
                    f"Monitor for further increase."
                )

            warnings.append({
                "train_id": train_id,
                "car_id": car["car_id"],
                "warning_type": warning_type,
                "severity": severity,
                "message": message,
                "timestamp": now.isoformat(),
                "is_active": True,
            })

    return warnings


# ─── Core Load Function ────────────────────────────────────────────────────────

def load_scenario(scenario_name: str, train_id: str = TRAIN_ID) -> Optional[Dict]:
    """
    Load a scenario into the State Manager with complete data:
    - Car occupancy (with camera IDs)
    - Predictions per car
    - Warnings for high/full cars
    - Recommendation if imbalanced
    - Camera status for all cameras
    - Decision history
    """
    scenario = SCENARIOS.get(scenario_name)
    if not scenario:
        return None

    state_manager.reset()
    pattern = scenario["pattern"]
    cars_data = scenario["cars"]

    # 1) Populate car occupancy with camera IDs
    for i, car_data in enumerate(cars_data):
        car_id = car_data["car_id"]
        passengers = car_data["passengers"]
        camera_id = f"car{str(car_id).zfill(2)}_cam01"

        state_manager.update_car_occupancy(
            train_id=train_id,
            car_id=car_id,
            detected_persons=passengers,
            capacity=CAPACITY_PER_CAR,
            camera_id=camera_id,
        )

    # 2) Set camera status for all 20 cameras
    for cam_id in CAMERA_IDS:
        state_manager.update_camera_status(cam_id, {
            "status": "online",
            "last_frame": datetime.utcnow().isoformat(),
            "fps": 15,
            "resolution": "640x480",
        })

    # 3) Generate and store warnings
    warnings = _generate_warnings(cars_data, train_id)
    for w_data in warnings:
        from app.schemas.occupancy import Warning
        warning = Warning(**w_data)
        state_manager._warnings.append(warning)

    # 4) Generate and store decisions
    recommendation = _generate_recommendation(cars_data)
    if recommendation:
        from app.schemas.occupancy import Decision
        decision = Decision(
            train_id=train_id,
            from_car_id=recommendation["fromCarId"],
            to_car_id=recommendation["toCarId"],
            action=recommendation["action"],
            confidence=recommendation["confidence"],
            reason=recommendation["reason"],
        )
        state_manager.add_decision(decision)

    return scenario


# ─── Broadcast Functions ───────────────────────────────────────────────────────

async def broadcast_full_state(train_id: str = TRAIN_ID):
    """
    Broadcast complete state to all WebSocket clients.
    Sends occupancy, predictions, warnings, recommendations, and camera status.
    """
    train_state = state_manager.get_train_state(train_id)
    if not train_state:
        return

    scenario_name = DEFAULT_SCENARIO
    pattern = SCENARIOS.get(scenario_name, {}).get("pattern", "peak")

    # Broadcast occupancy + prediction for each car
    for car in train_state.cars:
        pct = car.occupancy_percentage

        # Get matching pattern from loaded scenario
        scenario_cars = SCENARIOS.get(scenario_name, {}).get("cars", [])
        car_data = next((c for c in scenario_cars if c["car_id"] == car.car_id), None)
        if car_data:
            pattern = SCENARIOS.get(scenario_name, {}).get("pattern", "peak")
        else:
            pattern = "normal"

        prediction = _generate_prediction(car.car_id, pct, pattern)

        # Broadcast occupancy
        await integration_hub.broadcast_occupancy_updated(
            car_id=car.car_id,
            occupancy_data={
                "car_id": car.car_id,
                "occupancy_percentage": car.occupancy_percentage,
                "person_count": car.detected_persons,
                "capacity": car.capacity,
                "status": car.status,
                "risk_score": car.risk_score,
                "camera_id": car.camera_id or f"car{str(car.car_id).zfill(2)}_cam01",
            },
            train_id=train_id,
        )

        # Broadcast prediction
        await integration_hub.broadcast_prediction_updated(
            car_id=car.car_id,
            prediction=prediction,
            train_id=train_id,
        )

    # Broadcast camera status for all cameras
    for cam_id in CAMERA_IDS:
        await integration_hub.broadcast_camera_status_updated(
            camera_id=cam_id,
            status="online",
            train_id=train_id,
        )

    # Broadcast warnings
    warnings = state_manager.get_active_warnings(train_id)
    for warning in warnings:
        await integration_hub.broadcast_warning_updated(
            warning={
                "train_id": warning.train_id,
                "car_id": warning.car_id,
                "warning_type": warning.warning_type,
                "severity": warning.severity,
                "message": warning.message,
                "timestamp": warning.timestamp.isoformat() if warning.timestamp else datetime.utcnow().isoformat(),
                "is_active": warning.is_active,
            },
            train_id=train_id,
        )

    # Broadcast recommendation
    scenario_cars = SCENARIOS.get(DEFAULT_SCENARIO, {}).get("cars", [])
    recommendation = _generate_recommendation(scenario_cars)
    if recommendation:
        await integration_hub.broadcast_recommendation_changed(
            recommendation=recommendation,
            train_id=train_id,
        )

    # Broadcast system health
    summary = state_manager.get_system_summary()
    await integration_hub.broadcast_system_health_updated(
        health={
            "backend": "running",
            "ai": "loaded",
            "cameras": summary.get("activeCameras", 0),
            "uptime": summary.get("uptimeSeconds", 0),
            "activeWarnings": summary.get("activeWarnings", 0),
        },
        train_id=train_id,
    )


async def seed_default(train_id: str = TRAIN_ID):
    """
    Auto-seed default scenario on startup.
    Loads the default scenario and broadcasts the full initial state.
    """
    scenario = load_scenario(DEFAULT_SCENARIO, train_id)
    if not scenario:
        print(f"[SEED] Failed to load default scenario '{DEFAULT_SCENARIO}'")
        return

    car_count = len(scenario["cars"])
    total_passengers = sum(c["passengers"] for c in scenario["cars"])
    total_pct = (total_passengers / (CAPACITY_PER_CAR * TOTAL_CARS)) * 100
    status = _status(total_pct)

    warnings = state_manager.get_active_warnings(train_id)
    has_recommendation = _generate_recommendation(scenario["cars"]) is not None

    print(f"[SEED] Loaded '{DEFAULT_SCENARIO}' scenario")
    print(f"[SEED] Train: {train_id} ({FORMATION})")
    print(f"[SEED] Cars: {car_count}, Passengers: {total_passengers}/{CAPACITY_PER_CAR * TOTAL_CARS} ({total_pct:.1f}%)")
    print(f"[SEED] Status: {status}, Warnings: {len(warnings)}, Recommendation: {has_recommendation}")
    print(f"[SEED] Cameras: {len(CAMERA_IDS)} online")

    await broadcast_full_state(train_id)


# ─── Periodic Update Simulation ────────────────────────────────────────────────

async def simulate_occupancy_change(train_id: str = TRAIN_ID):
    """
    Simulate realistic occupancy fluctuation.
    Slightly adjusts passenger counts to simulate boarding/alighting.
    Called periodically to make the dashboard feel alive.
    """
    train_state = state_manager.get_train_state(train_id)
    if not train_state or not train_state.cars:
        return

    scenario = SCENARIOS.get(DEFAULT_SCENARIO, {})
    pattern = scenario.get("pattern", "peak")

    for car in train_state.cars:
        current_passengers = car.detected_persons
        # Small random fluctuation (-3 to +3 passengers)
        delta = random.randint(-3, 3)
        new_passengers = max(0, min(CAPACITY_PER_CAR + 20, current_passengers + delta))

        if new_passengers != current_passengers:
            state_manager.update_car_occupancy(
                train_id=train_id,
                car_id=car.car_id,
                detected_persons=new_passengers,
                capacity=CAPACITY_PER_CAR,
                camera_id=car.camera_id or f"car{str(car.car_id).zfill(2)}_cam01",
            )

            # Broadcast the update
            updated_car = next(
                (c for c in state_manager.get_train_state(train_id).cars if c.car_id == car.car_id),
                None,
            )
            if updated_car:
                prediction = _generate_prediction(car.car_id, updated_car.occupancy_percentage, pattern)

                await integration_hub.broadcast_occupancy_updated(
                    car_id=car.car_id,
                    occupancy_data={
                        "car_id": car.car_id,
                        "occupancy_percentage": updated_car.occupancy_percentage,
                        "person_count": updated_car.detected_persons,
                        "capacity": updated_car.capacity,
                        "status": updated_car.status,
                        "risk_score": updated_car.risk_score,
                        "camera_id": updated_car.camera_id,
                    },
                    train_id=train_id,
                )

                await integration_hub.broadcast_prediction_updated(
                    car_id=car.car_id,
                    prediction=prediction,
                    train_id=train_id,
                )
