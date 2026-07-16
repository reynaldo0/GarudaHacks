from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager

router = APIRouter()

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


@router.post("/simulation/reset")
async def reset_simulation():
    """
    Reset simulation to initial state.
    """
    state_manager.reset()
    return {
        "success": True,
        "data": {
            "message": "Simulation reset successfully",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.post("/simulation/scenario/{scenario_name}")
async def load_scenario(scenario_name: str):
    """
    Load a predefined simulation scenario.
    """
    if scenario_name not in SCENARIOS:
        return {
            "success": False,
            "error": f"Invalid scenario. Valid: {list(SCENARIOS.keys())}",
        }

    scenario = SCENARIOS[scenario_name]
    state_manager.reset()

    for car_data in scenario["cars"]:
        state_manager.update_car_occupancy(
            train_id="SF10-001",
            car_id=car_data["car_id"],
            detected_persons=car_data["passengers"],
            capacity=200,
        )

    return {
        "success": True,
        "data": {
            "scenario": scenario_name,
            "description": scenario["description"],
            "cars_loaded": len(scenario["cars"]),
            "message": f"Scenario '{scenario_name}' loaded",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status."""
    summary = state_manager.get_system_summary()
    return {
        "success": True,
        "data": {
            "active": summary["trains"] > 0,
            "trains_loaded": summary["trains"],
            "active_warnings": summary["active_warnings"],
            "total_decisions": summary["total_decisions"],
            "uptime_seconds": summary["uptime_seconds"],
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
