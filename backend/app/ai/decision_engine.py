"""
PROJECT THEMIS - Decision Engine
Version: 6.0

Generates warnings, decisions, and door recommendations based on spatial occupancy.
"""

from typing import Dict, List, Optional
from loguru import logger
from app.schemas.occupancy import Warning, Decision


class DecisionEngine:
    """Generates warnings and decisions from spatial occupancy data."""

    def __init__(self):
        pass

    def evaluate(self, car_data: Dict, train_id: str = "SF6-001") -> Optional[Warning]:
        """
        Evaluate car data and generate warning if needed.
        """
        density_indicator = car_data.get("density_indicator", "GREEN")
        car_id = car_data.get("car_id", 0)
        occupancy_ratio = car_data.get("occupancy_ratio", 0)

        if density_indicator == "RED":
            return Warning(
                train_id=train_id,
                car_id=car_id,
                warning_type="RED_DENSITY",
                severity="CRITICAL",
                message=f"Car {car_id} is RED density (occupancy: {occupancy_ratio:.1%})",
            )
        elif density_indicator == "YELLOW":
            return Warning(
                train_id=train_id,
                car_id=car_id,
                warning_type="YELLOW_DENSITY",
                severity="WARNING",
                message=f"Car {car_id} is YELLOW density (occupancy: {occupancy_ratio:.1%})",
            )

        return None

    def generate_redistribution_decision(
        self,
        train_id: str,
        from_car_id: int,
        to_car_id: int,
        confidence: float,
        reason: str,
    ) -> Decision:
        """Generate a redistribution decision."""
        return Decision(
            train_id=train_id,
            from_car_id=from_car_id,
            to_car_id=to_car_id,
            action="REDISTRIBUTION",
            confidence=confidence,
            reason=reason,
        )

    def generate_door_decision(
        self,
        train_id: str,
        car_id: int,
        door_action: str,
        reason: str,
    ) -> Decision:
        """Generate a door action decision."""
        return Decision(
            train_id=train_id,
            from_car_id=car_id,
            to_car_id=None,
            action=f"DOOR_{door_action}",
            door_action=door_action,
            confidence=0.95,
            reason=reason,
        )

    def get_led_state(self, density_indicator: str) -> str:
        """Get LED state from density indicator."""
        led_map = {
            "GREEN": "GREEN",
            "YELLOW": "YELLOW",
            "RED": "RED",
        }
        return led_map.get(density_indicator, "OFF")

    def get_audio_event(self, density_indicator: str) -> Optional[str]:
        """Get audio event from density indicator."""
        audio_map = {
            "YELLOW": "warning_chime",
            "RED": "alert_tone",
        }
        return audio_map.get(density_indicator)
