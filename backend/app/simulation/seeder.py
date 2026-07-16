"""
PROJECT THEMIS - Simulation Seeder
Version: 5.0

Seeder for dummy occupancy data. Auto-loads a default scenario on backend
startup so the Operation Center dashboard and Unity Digital Twin have live
data immediately - no manual scenario load required.
"""

from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub

SCENARIOS = {
    "empty": {"description": "Empty train", "cars": []},
    "normal": {
        "description": "Normal operation",
        "cars": [
            {"car_id": 1, "passengers": 80},
            {"car_id": 2, "passengers": 100},
            {"car_id": 3, "passengers": 120},
            {"car_id": 4, "passengers": 140},
            {"car_id": 5, "passengers": 90},
            {"car_id": 6, "passengers": 70},
            {"car_id": 7, "passengers": 110},
            {"car_id": 8, "passengers": 85},
            {"car_id": 9, "passengers": 95},
            {"car_id": 10, "passengers": 60},
        ],
    },
    "peak_hour": {
        "description": "Rush hour congestion",
        "cars": [
            {"car_id": 1, "passengers": 160},
            {"car_id": 2, "passengers": 175},
            {"car_id": 3, "passengers": 190},
            {"car_id": 4, "passengers": 200},
            {"car_id": 5, "passengers": 130},
            {"car_id": 6, "passengers": 80},
            {"car_id": 7, "passengers": 150},
            {"car_id": 8, "passengers": 120},
            {"car_id": 9, "passengers": 170},
            {"car_id": 10, "passengers": 100},
        ],
    },
    "holiday": {
        "description": "Holiday light traffic",
        "cars": [
            {"car_id": 1, "passengers": 30},
            {"car_id": 2, "passengers": 45},
            {"car_id": 3, "passengers": 25},
            {"car_id": 4, "passengers": 50},
            {"car_id": 5, "passengers": 35},
            {"car_id": 6, "passengers": 20},
            {"car_id": 7, "passengers": 40},
            {"car_id": 8, "passengers": 55},
            {"car_id": 9, "passengers": 30},
            {"car_id": 10, "passengers": 25},
        ],
    },
}

DEFAULT_SCENARIO = "peak_hour"


def load_scenario(scenario_name: str, train_id: str = "SF10-001") -> dict:
    """Load a scenario into the State Manager. Returns the scenario dict."""
    scenario = SCENARIOS.get(scenario_name)
    if not scenario:
        return None

    state_manager.reset()
    for car_data in scenario["cars"]:
        state_manager.update_car_occupancy(
            train_id=train_id,
            car_id=car_data["car_id"],
            detected_persons=car_data["passengers"],
            capacity=200,
        )
    return scenario


async def seed_default(train_id: str = "SF10-001"):
    """Auto-seed default scenario on startup and broadcast the initial state."""
    scenario = load_scenario(DEFAULT_SCENARIO, train_id)
    if not scenario:
        return

    print(f"[SEED] Loaded default scenario '{DEFAULT_SCENARIO}' ({len(scenario['cars'])} cars)")

    train_state = state_manager.get_train_state(train_id)
    if train_state:
        for car in train_state.cars:
            await integration_hub.broadcast_occupancy_updated(
                car_id=car.car_id,
                occupancy_data={
                    "car_id": car.car_id,
                    "occupancy_percentage": car.occupancy_percentage,
                    "person_count": car.detected_persons,
                    "capacity": car.capacity,
                    "status": car.status,
                    "risk_score": car.risk_score,
                },
                train_id=train_id,
            )