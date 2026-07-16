"""
PROJECT THEMIS - Door Engine
Version: 6.0

Door automation logic based on spatial occupancy and redistribution.
"""

from typing import Dict, Optional
from loguru import logger

from app.config.settings import settings


class DoorEngine:
    """
    Door Automation Engine.

    Rule: IF density_indicator == "RED"
          AND recommended_target exists
          AND target occupancy < current occupancy
          THEN door_action = "OPEN_MIDDLE"

    ELSE: door_action = "CLOSE"

    Note: In digital twin, this is a simulation.
    In production, this would go through Safety Chain before execution.
    """

    def __init__(self):
        self.open_on_red = settings.DOOR_MIDDLE_OPEN_ON_RED

    def evaluate(
        self,
        car_id: int,
        density_indicator: str,
        redistribution: Optional[Dict] = None,
    ) -> Dict:
        """
        Evaluate door action based on density and redistribution.

        Args:
            car_id: Current car ID
            density_indicator: GREEN, YELLOW, RED
            redistribution: Optional redistribution recommendation

        Returns:
            Dict with door_action, reason
        """
        door_action = "CLOSE"
        reason = "Default state"

        if self.open_on_red and density_indicator == "RED":
            if redistribution and redistribution.get("to_car_id"):
                # There is a valid redistribution target
                target_occupancy = redistribution.get("to_occupancy", 0)
                if target_occupancy < 0.7:  # Target has capacity
                    door_action = "OPEN_MIDDLE"
                    reason = f"RED density with redistribution target Car {redistribution.get('to_car_id')} ({target_occupancy:.0%})"
                else:
                    reason = f"RED density but target Car {redistribution.get('to_car_id')} is also busy ({target_occupancy:.0%})"
            else:
                # RED but no redistribution target available
                reason = "RED density but no valid redistribution target"

        elif density_indicator == "YELLOW":
            reason = "YELLOW density - door remains closed, monitoring"

        elif density_indicator == "GREEN":
            reason = "GREEN density - no action needed"

        return {
            "car_id": car_id,
            "door_action": door_action,
            "density_indicator": density_indicator,
            "reason": reason,
            "timestamp": None,  # Will be set by caller
        }

    def get_door_state(self, door_action: str) -> Dict:
        """
        Get door state for visualization.

        Returns:
            Dict with is_open, animation_state
        """
        if door_action == "OPEN_MIDDLE":
            return {
                "is_open": True,
                "animation_state": "OPENING",
                "door_position": "MIDDLE",
            }
        else:
            return {
                "is_open": False,
                "animation_state": "CLOSING",
                "door_position": "MIDDLE",
            }
