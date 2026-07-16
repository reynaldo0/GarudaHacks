"""
PROJECT THEMIS - Announcement Engine
Version: 6.0

Generates announcements based on redistribution recommendations.
"""

from typing import Dict, Optional
from loguru import logger


class AnnouncementEngine:
    """
    Announcement Generator.

    Generates announcements AFTER redistribution recommendation.

    Example:
    "Carriage 6 has available capacity.
    Passengers are advised to move to Carriage 6."
    """

    def __init__(self):
        pass

    def generate(self, redistribution: Optional[Dict] = None, car_id: int = 0) -> Optional[Dict]:
        """
        Generate announcement based on redistribution.

        Args:
            redistribution: Redistribution recommendation dict
            car_id: Current car ID

        Returns:
            Dict with announcement text and type, or None
        """
        if not redistribution:
            return None

        action = redistribution.get("action", "")
        to_car_id = redistribution.get("to_car_id") or redistribution.get("least_occupied_car")

        if not to_car_id:
            return None

        if action in ("REDISTRIBUTION", "GLOBAL_REDISTRIBUTION"):
            return self._generate_redistribution_announcement(
                from_car_id=car_id,
                to_car_id=to_car_id,
                redistribution=redistribution,
            )

        return None

    def _generate_redistribution_announcement(
        self,
        from_car_id: int,
        to_car_id: int,
        redistribution: Dict,
    ) -> Dict:
        """Generate redistribution announcement."""
        to_occupancy = redistribution.get("to_occupancy", 0)
        available_pct = round((1.0 - to_occupancy) * 100)

        text = (
            f"Carriage {to_car_id} has available capacity ({available_pct}% free). "
            f"Passengers in Carriage {from_car_id} are advised to move to Carriage {to_car_id}."
        )

        return {
            "type": "REDISTRIBUTION",
            "text": text,
            "from_car_id": from_car_id,
            "to_car_id": to_car_id,
            "priority": "HIGH",
        }
