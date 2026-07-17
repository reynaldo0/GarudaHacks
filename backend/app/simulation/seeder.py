"""
PROJECT THEMIS - Simulation Seeder
Version: 6.0

Comprehensive data seeder with realistic KRL Commuter Line data patterns.
Populates the State Manager with spatial occupancy data for the SF6 formation.
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub

# ─── SF6 Formation Constants ──────────────────────────────────────────────────
TRAIN_ID = "SF6-001"
TOTAL_CARS = 6
FORMATION = "SF6"
FLOOR_AREA_M2 = 42.0

# Camera IDs: 4 ceiling fisheye cameras per car
CAMERA_IDS = [
    f"car{str(i).zfill(2)}_cam{str(j).zfill(2)}"
    for i in range(1, TOTAL_CARS + 1)
    for j in (1, 2, 3, 4)
]


# ─── Density Indicator ────────────────────────────────────────────────────────
def _density_indicator(occupancy_ratio: float) -> str:
    if occupancy_ratio < 0.4:
        return "GREEN"
    elif occupancy_ratio < 0.7:
        return "YELLOW"
    else:
        return "RED"


# ─── Scenario Definitions ──────────────────────────────────────────────────────
SCENARIOS = {
    "empty": {
        "description": "Empty train - no passengers",
        "pattern": "empty",
        "cars": [{"car_id": i, "occupancy_ratio": 0.0} for i in range(1, 7)],
    },
    "normal": {
        "description": "Normal operation - balanced mid-day traffic",
        "pattern": "normal",
        "cars": [
            {"car_id": 1, "occupancy_ratio": 0.38},
            {"car_id": 2, "occupancy_ratio": 0.42},
            {"car_id": 3, "occupancy_ratio": 0.35},
            {"car_id": 4, "occupancy_ratio": 0.40},
            {"car_id": 5, "occupancy_ratio": 0.33},
            {"car_id": 6, "occupancy_ratio": 0.30},
        ],
    },
    "peak_hour": {
        "description": "Rush hour congestion - morning/evening peak",
        "pattern": "peak",
        "cars": [
            {"car_id": 1, "occupancy_ratio": 0.88},
            {"car_id": 2, "occupancy_ratio": 0.80},
            {"car_id": 3, "occupancy_ratio": 0.92},
            {"car_id": 4, "occupancy_ratio": 0.97},
            {"car_id": 5, "occupancy_ratio": 0.72},
            {"car_id": 6, "occupancy_ratio": 0.65},
        ],
    },
    "holiday": {
        "description": "Holiday - light recreational traffic",
        "pattern": "holiday",
        "cars": [
            {"car_id": 1, "occupancy_ratio": 0.18},
            {"car_id": 2, "occupancy_ratio": 0.14},
            {"car_id": 3, "occupancy_ratio": 0.22},
            {"car_id": 4, "occupancy_ratio": 0.12},
            {"car_id": 5, "occupancy_ratio": 0.09},
            {"car_id": 6, "occupancy_ratio": 0.07},
        ],
    },
    "imbalanced": {
        "description": "Heavy imbalance - test redistribution engine",
        "pattern": "imbalanced",
        "cars": [
            {"car_id": 1, "occupancy_ratio": 0.97},
            {"car_id": 2, "occupancy_ratio": 0.94},
            {"car_id": 3, "occupancy_ratio": 0.90},
            {"car_id": 4, "occupancy_ratio": 0.20},
            {"car_id": 5, "occupancy_ratio": 0.10},
            {"car_id": 6, "occupancy_ratio": 0.05},
        ],
    },
    "emergency": {
        "description": "Emergency scenario - multiple RED density cars",
        "pattern": "emergency",
        "cars": [
            {"car_id": 1, "occupancy_ratio": 0.99},
            {"car_id": 2, "occupancy_ratio": 0.96},
            {"car_id": 3, "occupancy_ratio": 0.93},
            {"car_id": 4, "occupancy_ratio": 0.90},
            {"car_id": 5, "occupancy_ratio": 0.88},
            {"car_id": 6, "occupancy_ratio": 0.85},
        ],
    },
}

DEFAULT_SCENARIO = "peak_hour"


# ─── Prediction Generator ──────────────────────────────────────────────────────

def _generate_prediction(car_id: int, current_ratio: float, pattern: str) -> Dict:
    """Generate realistic occupancy prediction."""
    rng = random.Random(car_id + int(time.time()) % 100)

    if pattern == "empty":
        trend = "stable"
        predicted = 0.0
        confidence = 0.95
    elif pattern == "normal":
        delta = rng.uniform(-0.03, 0.05)
        predicted = max(0.0, min(1.0, current_ratio + delta))
        trend = "increasing" if delta > 0.02 else "decreasing" if delta < -0.02 else "stable"
        confidence = round(rng.uniform(0.70, 0.88), 2)
    elif pattern == "peak":
        delta = rng.uniform(0.01, 0.08)
        predicted = max(0.0, min(1.0, current_ratio + delta))
        trend = "increasing"
        confidence = round(rng.uniform(0.72, 0.90), 2)
    elif pattern == "holiday":
        delta = rng.uniform(-0.04, 0.02)
        predicted = max(0.0, min(1.0, current_ratio + delta))
        trend = "decreasing" if delta < -0.01 else "stable"
        confidence = round(rng.uniform(0.75, 0.92), 2)
    elif pattern == "imbalanced":
        if current_ratio > 0.7:
            delta = rng.uniform(0.02, 0.06)
            trend = "increasing"
        else:
            delta = rng.uniform(-0.02, 0.01)
            trend = "stable" if abs(delta) < 0.01 else "decreasing"
        predicted = max(0.0, min(1.0, current_ratio + delta))
        confidence = round(rng.uniform(0.68, 0.85), 2)
    elif pattern == "emergency":
        delta = rng.uniform(0.02, 0.10)
        predicted = max(0.0, min(1.0, current_ratio + delta))
        trend = "increasing"
        confidence = round(rng.uniform(0.80, 0.95), 2)
    else:
        predicted = current_ratio
        trend = "stable"
        confidence = 0.5

    return {
        "trend": trend,
        "predictedOccupancyRatio": round(predicted, 4),
        "confidence": confidence,
        "horizonMinutes": 15,
    }


# ─── Recommendation Generator ──────────────────────────────────────────────────

def _generate_recommendation(cars_data: List[Dict]) -> Optional[Dict]:
    """Generate redistribution recommendation if significant imbalance exists."""
    if not cars_data:
        return None

    sorted_cars = sorted(cars_data, key=lambda c: c["occupancy_ratio"], reverse=True)
    most_crowded = sorted_cars[0]
    least_crowded = sorted_cars[-1]

    most_occ = most_crowded["occupancy_ratio"]
    least_occ = least_crowded["occupancy_ratio"]
    imbalance = most_occ - least_occ

    if imbalance > 0.2 and most_occ > 0.6:
        confidence = min(0.95, imbalance)
        return {
            "action": "REDISTRIBUTION",
            "fromCarId": most_crowded["car_id"],
            "toCarId": least_crowded["car_id"],
            "confidence": round(confidence, 2),
            "reason": (
                f"Car {most_crowded['car_id']} is at {most_occ:.0%} occupancy. "
                f"Car {least_crowded['car_id']} has available space at {least_occ:.0%}. "
                f"Passengers should move to balance occupancy."
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    return None


# ─── Warning Generator ─────────────────────────────────────────────────────────

def _generate_warnings(cars_data: List[Dict], train_id: str) -> List[Dict]:
    """Generate warnings for RED density cars."""
    warnings = []
    now = datetime.utcnow()

    for car in cars_data:
        indicator = _density_indicator(car["occupancy_ratio"])

        if indicator == "RED":
            warnings.append({
                "train_id": train_id,
                "car_id": car["car_id"],
                "warning_type": "RED_DENSITY",
                "severity": "CRITICAL",
                "message": f"Car {car['car_id']} is RED density (occupancy: {car['occupancy_ratio']:.0%})",
                "timestamp": now.isoformat(),
                "is_active": True,
            })
        elif indicator == "YELLOW":
            warnings.append({
                "train_id": train_id,
                "car_id": car["car_id"],
                "warning_type": "YELLOW_DENSITY",
                "severity": "WARNING",
                "message": f"Car {car['car_id']} is YELLOW density (occupancy: {car['occupancy_ratio']:.0%})",
                "timestamp": now.isoformat(),
                "is_active": True,
            })

    return warnings


# ─── Core Load Function ────────────────────────────────────────────────────────

def load_scenario(scenario_name: str, train_id: str = TRAIN_ID) -> Optional[Dict]:
    """Load a scenario into the State Manager with spatial occupancy data."""
    scenario = SCENARIOS.get(scenario_name)
    if not scenario:
        return None

    state_manager.reset()
    pattern = scenario["pattern"]
    cars_data = scenario["cars"]

    # Populate car spatial occupancy
    for car_data in cars_data:
        car_id = car_data["car_id"]
        occ_ratio = car_data["occupancy_ratio"]
        free_space = 1.0 - occ_ratio
        indicator = _density_indicator(occ_ratio)
        camera_id = f"car{str(car_id).zfill(2)}_cam01"

        state_manager.update_car_spatial_occupancy(
            train_id=train_id,
            car_id=car_id,
            occupancy_ratio=occ_ratio,
            free_space_ratio=free_space,
            spatial_occupancy_score=occ_ratio,
            density_indicator=indicator,
            camera_id=camera_id,
        )

    # Set camera status for all 24 cameras
    for cam_id in CAMERA_IDS:
        state_manager.update_camera_status(cam_id, {
            "status": "online",
            "last_frame": datetime.utcnow().isoformat(),
            "fps": 1,
            "resolution": "640x640",
            "type": "ceiling_fisheye",
        })

    # Generate and store warnings
    warnings = _generate_warnings(cars_data, train_id)
    for w_data in warnings:
        from app.schemas.occupancy import Warning
        warning = Warning(**w_data)
        state_manager._warnings.append(warning)

    # Generate and store decisions
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
    """Broadcast complete PipelineState to all WebSocket clients."""
    train_state = state_manager.get_train_state(train_id)
    if not train_state:
        return

    scenario_name = DEFAULT_SCENARIO
    pattern = SCENARIOS.get(scenario_name, {}).get("pattern", "peak")

    # Broadcast PipelineState for each car
    for car in train_state.cars:
        occ_ratio = getattr(car, 'occupancy_ratio', 0)
        indicator = getattr(car, 'density_indicator', 'GREEN')

        # Get prediction
        prediction = _generate_prediction(car.car_id, occ_ratio, pattern)

        # Build PipelineState
        pipeline_state = {
            "car_id": f"car_{car.car_id:02d}",
            "occupancy_ratio": occ_ratio,
            "free_space_ratio": getattr(car, 'free_space_ratio', 1.0),
            "density_indicator": indicator,
            "spatial_occupancy_score": getattr(car, 'spatial_occupancy_score', 0),
            "recommended_target": None,
            "door_action": "CLOSE",
            "announcement": None,
            "cales_score": 0.0,
            "health_index": 100.0,
            "damage_multiplier": 1.0,
            "inspection_priority": 0,
            "recommended_action": "CONTINUE_MONITORING",
            "prediction": prediction,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await integration_hub.broadcast_pipeline_state_updated(
            pipeline_state=pipeline_state,
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
    """Auto-seed default scenario on startup."""
    scenario = load_scenario(DEFAULT_SCENARIO, train_id)
    if not scenario:
        print(f"[SEED] Failed to load default scenario '{DEFAULT_SCENARIO}'")
        return

    car_count = len(scenario["cars"])
    avg_occupancy = sum(c["occupancy_ratio"] for c in scenario["cars"]) / car_count if car_count > 0 else 0
    indicator = _density_indicator(avg_occupancy)

    warnings = state_manager.get_active_warnings(train_id)
    has_recommendation = _generate_recommendation(scenario["cars"]) is not None

    print(f"[SEED] Loaded '{DEFAULT_SCENARIO}' scenario")
    print(f"[SEED] Train: {train_id} ({FORMATION})")
    print(f"[SEED] Cars: {car_count}, Avg Occupancy: {avg_occupancy:.0%}")
    print(f"[SEED] Indicator: {indicator}, Warnings: {len(warnings)}, Recommendation: {has_recommendation}")
    print(f"[SEED] Cameras: {len(CAMERA_IDS)} ceiling fisheye cameras online")

    await broadcast_full_state(train_id)


# ─── Periodic Update Simulation ────────────────────────────────────────────────

async def simulate_occupancy_change(train_id: str = TRAIN_ID):
    """Simulate realistic occupancy fluctuation."""
    train_state = state_manager.get_train_state(train_id)
    if not train_state or not train_state.cars:
        return

    scenario = SCENARIOS.get(DEFAULT_SCENARIO, {})
    pattern = scenario.get("pattern", "peak")

    for car in train_state.cars:
        current_ratio = getattr(car, 'occupancy_ratio', 0)
        # Small random fluctuation
        delta = random.uniform(-0.03, 0.03)
        new_ratio = max(0.0, min(1.0, current_ratio + delta))

        if abs(new_ratio - current_ratio) > 0.001:
            indicator = _density_indicator(new_ratio)
            state_manager.update_car_spatial_occupancy(
                train_id=train_id,
                car_id=car.car_id,
                occupancy_ratio=new_ratio,
                free_space_ratio=1.0 - new_ratio,
                spatial_occupancy_score=new_ratio,
                density_indicator=indicator,
                camera_id=car.camera_id or f"car{str(car.car_id).zfill(2)}_cam01",
            )

            # Build and broadcast PipelineState
            prediction = _generate_prediction(car.car_id, new_ratio, pattern)

            pipeline_state = {
                "car_id": f"car_{car.car_id:02d}",
                "occupancy_ratio": round(new_ratio, 4),
                "free_space_ratio": round(1.0 - new_ratio, 4),
                "density_indicator": indicator,
                "spatial_occupancy_score": round(new_ratio, 4),
                "recommended_target": None,
                "door_action": "CLOSE",
                "announcement": None,
                "cales_score": 0.0,
                "health_index": 100.0,
                "damage_multiplier": 1.0,
                "inspection_priority": 0,
                "recommended_action": "CONTINUE_MONITORING",
                "prediction": prediction,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await integration_hub.broadcast_pipeline_state_updated(
                pipeline_state=pipeline_state,
                train_id=train_id,
            )
