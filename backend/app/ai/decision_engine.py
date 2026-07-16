"""
PROJECT THEMIS - Decision Engine
Version: 5.0

Generates warnings, alerts, and final decisions.
"""

from typing import Dict, List, Optional
from loguru import logger
from app.schemas.occupancy import Warning, Decision


class DecisionEngine:
    """Generates warnings and decisions from occupancy data."""

    def __init__(self):
        pass

    def evaluate(self, car_data: Dict, train_id: str = "SF10-001") -> Optional[Warning]:
        """
        Evaluate car data and generate warning if needed.
        """
        status = car_data.get("status", "LOW")
        car_id = car_data.get("car_id", 0)
        occupancy_pct = car_data.get("occupancy_percentage", 0)

        if status in ("HIGH", "FULL", "OVERCAPACITY"):
            severity = "CRITICAL" if status in ("FULL", "OVERCAPACITY") else "WARNING"
            message = f"Car {car_id} is {status} ({occupancy_pct}%)"

            return Warning(
                train_id=train_id,
                car_id=car_id,
                warning_type=f"{status}_OCCUPANCY",
                severity=severity,
                message=message,
            )

        return None

    def generate_decision(
        self,
        train_id: str,
        from_car_id: int,
        to_car_id: int,
        confidence: float,
        reason: str,
    ) -> Decision:
        """Generate a decision/recommendation."""
        return Decision(
            train_id=train_id,
            from_car_id=from_car_id,
            to_car_id=to_car_id,
            action="MOVE_PASSENGER",
            confidence=confidence,
            reason=reason,
        )

    def get_led_state(self, status: str) -> str:
        """Get LED state from occupancy status."""
        led_map = {
            "LOW": "GREEN",
            "NORMAL": "GREEN",
            "HIGH": "YELLOW",
            "FULL": "RED",
            "OVERCAPACITY": "RED_BLINK",
        }
        return led_map.get(status, "OFF")

    def get_audio_event(self, status: str) -> Optional[str]:
        """Get audio event from occupancy status."""
        audio_map = {
            "HIGH": "warning_chime",
            "FULL": "alert_tone",
            "OVERCAPACITY": "emergency_alert",
        }
        return audio_map.get(status)
