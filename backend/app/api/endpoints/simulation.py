"""
PROJECT THEMIS - Simulation Endpoint
Version: 5.0

This endpoint controls simulation mode.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub
from app.simulation.seeder import SCENARIOS, load_scenario, broadcast_full_state

router = APIRouter()


@router.post("/simulation/reset")
async def reset_simulation():
    """Reset simulation to initial state."""
    state_manager.reset()
    await integration_hub.broadcast_simulation_reset("Simulation reset")
    return {
        "success": True,
        "data": {
            "message": "Simulation reset successfully",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.post("/simulation/scenario/{scenario_name}")
async def load_scenario_endpoint(scenario_name: str):
    """Load a predefined simulation scenario with full state broadcast."""
    if scenario_name not in SCENARIOS:
        return {
            "success": False,
            "error": f"Invalid scenario. Valid: {list(SCENARIOS.keys())}",
        }

    scenario = load_scenario(scenario_name)
    if not scenario:
        return {"success": False, "error": "Scenario load failed"}

    # Broadcast full state (occupancy + predictions + warnings + cameras)
    await broadcast_full_state("SF6-001")

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
            "trainsLoaded": summary["trains"],
            "activeWarnings": summary["activeWarnings"],
            "totalDecisions": summary["totalDecisions"],
            "uptimeSeconds": summary["uptimeSeconds"],
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
