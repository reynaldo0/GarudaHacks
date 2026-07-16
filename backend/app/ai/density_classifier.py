"""
PROJECT THEMIS - Density Classifier
Version: 6.0

Classifies spatial occupancy into density indicators.
"""

from typing import Dict
from loguru import logger

from app.config.settings import settings


class DensityClassifier:
    """
    Classifies spatial occupancy into density indicators:
    - GREEN: High free space (low density)
    - YELLOW: Moderate free space (medium density)
    - RED: Low free space (high density)
    """

    def __init__(self):
        self.green_threshold = settings.DENSITY_GREEN_THRESHOLD
        self.yellow_threshold = settings.DENSITY_YELLOW_THRESHOLD
        self.red_threshold = settings.DENSITY_RED_THRESHOLD

    def classify(self, occupancy_metrics: Dict) -> Dict:
        """
        Classify occupancy metrics into density indicator.

        Args:
            occupancy_metrics: Dict with 'free_space_ratio' or 'occupancy_ratio'

        Returns:
            Dict with:
                - density_indicator: str (GREEN, YELLOW, RED)
                - confidence: float
                - reason: str
        """
        # Prefer free_space_ratio, fallback to occupancy_ratio
        free_space = occupancy_metrics.get("free_space_ratio", None)
        if free_space is None:
            occupancy_ratio = occupancy_metrics.get("occupancy_ratio", 0.0)
            free_space = 1.0 - occupancy_ratio

        indicator, confidence, reason = self._classify_from_free_space(free_space)

        return {
            "density_indicator": indicator,
            "free_space_ratio": round(float(free_space), 4),
            "confidence": round(float(confidence), 4),
            "reason": reason,
        }

    def _classify_from_free_space(self, free_space: float) -> tuple:
        """
        Classify based on free space ratio.

        Thresholds:
            - free_space > GREEN_THRESHOLD (0.6) -> GREEN
            - free_space > YELLOW_THRESHOLD (0.3) -> YELLOW
            - free_space <= YELLOW_THRESHOLD -> RED
        """
        if free_space > self.green_threshold:
            return ("GREEN", 0.9, "High free space available")
        elif free_space > self.yellow_threshold:
            return ("YELLOW", 0.8, "Moderate free space remaining")
        elif free_space > self.red_threshold:
            return ("RED", 0.85, "Low free space, high density")
        else:
            return ("RED", 0.95, "Very low free space, critical density")

    def classify_from_occupancy_ratio(self, occupancy_ratio: float) -> Dict:
        """
        Classify from occupancy ratio directly.

        Args:
            occupancy_ratio: float (0.0 - 1.0)

        Returns:
            Dict with density_indicator, confidence, reason
        """
        free_space = 1.0 - occupancy_ratio
        indicator, confidence, reason = self._classify_from_free_space(free_space)

        return {
            "density_indicator": indicator,
            "occupancy_ratio": round(float(occupancy_ratio), 4),
            "free_space_ratio": round(float(free_space), 4),
            "confidence": round(float(confidence), 4),
            "reason": reason,
        }
