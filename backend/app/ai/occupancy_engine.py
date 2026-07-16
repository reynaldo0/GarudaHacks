"""
PROJECT THEMIS - Occupancy Engine
Version: 6.0

Calculates occupancy from spatial segmentation results.
"""

from typing import Dict
from loguru import logger
from app.config.settings import settings


class OccupancyEngine:
    """Calculates occupancy metrics from spatial occupancy data."""

    def __init__(self, floor_area_m2: float = None):
        self.floor_area_m2 = floor_area_m2 or settings.FLOOR_AREA_M2

    def calculate(self, spatial_occupancy_score: float, free_space_ratio: float = None) -> Dict:
        """
        Calculate occupancy from spatial occupancy score.

        Args:
            spatial_occupancy_score: float (0.0 - 1.0) from spatial segmentation
            free_space_ratio: float (0.0 - 1.0) optional override

        Returns:
            Dict with occupancy_ratio, free_space_ratio, density_indicator, risk_score
        """
        occupancy_ratio = spatial_occupancy_score
        if free_space_ratio is None:
            free_space_ratio = 1.0 - occupancy_ratio

        density_indicator = self._determine_density(occupancy_ratio)
        risk_score = self._calculate_risk(occupancy_ratio)

        return {
            "occupancy_ratio": round(float(occupancy_ratio), 4),
            "free_space_ratio": round(float(free_space_ratio), 4),
            "density_indicator": density_indicator,
            "risk_score": round(float(risk_score), 4),
            "floor_area_m2": self.floor_area_m2,
        }

    def _determine_density(self, occupancy_ratio: float) -> str:
        """
        Determine density indicator from occupancy ratio.

        Thresholds:
            - occupancy < 0.4 -> GREEN (lots of free space)
            - occupancy 0.4 - 0.7 -> YELLOW (moderate)
            - occupancy > 0.7 -> RED (high density)
        """
        if occupancy_ratio < 0.4:
            return "GREEN"
        elif occupancy_ratio < 0.7:
            return "YELLOW"
        else:
            return "RED"

    def _calculate_risk(self, occupancy_ratio: float) -> float:
        """Calculate risk score from occupancy ratio."""
        if occupancy_ratio < 0.4:
            return 0.1
        elif occupancy_ratio < 0.7:
            return 0.4
        elif occupancy_ratio < 0.9:
            return 0.7
        else:
            return 1.0
