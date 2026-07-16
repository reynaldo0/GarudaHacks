"""
PROJECT THEMIS - Occupancy Engine
Version: 5.0

Calculates occupancy from YOLO detections.
"""

from typing import Dict, List
from loguru import logger
from app.config.settings import settings


class OccupancyEngine:
    """Calculates occupancy percentage and status from person detections."""

    def __init__(self, default_capacity: int = 200):
        self.default_capacity = default_capacity

    def calculate(self, person_count: int, capacity: int = None) -> Dict:
        """
        Calculate occupancy from person count.
        Returns occupancy percentage, status, risk score.
        """
        cap = capacity or self.default_capacity
        if cap <= 0:
            cap = 200

        occupancy_pct = (person_count / cap) * 100
        status = self._determine_status(occupancy_pct)
        risk_score = self._calculate_risk(occupancy_pct)

        return {
            "person_count": person_count,
            "capacity": cap,
            "occupancy_percentage": round(occupancy_pct, 2),
            "status": status,
            "risk_score": round(risk_score, 2),
        }

    def _determine_status(self, occupancy_pct: float) -> str:
        """Determine occupancy status from percentage."""
        if occupancy_pct < 40:
            return "LOW"
        elif occupancy_pct < 70:
            return "NORMAL"
        elif occupancy_pct < 90:
            return "HIGH"
        elif occupancy_pct <= 100:
            return "FULL"
        else:
            return "OVERCAPACITY"

    def _calculate_risk(self, occupancy_pct: float) -> float:
        """Calculate risk score from occupancy percentage."""
        if occupancy_pct < 40:
            return 0.1
        elif occupancy_pct < 70:
            return 0.3
        elif occupancy_pct < 90:
            return 0.7
        elif occupancy_pct <= 100:
            return 0.9
        else:
            return 1.0
