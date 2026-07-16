"""
PROJECT THEMIS - Redistribution Engine
Version: 6.0

Analyzes spatial occupancy across all cars and recommends redistribution.
"""

from typing import Dict, List, Optional
from loguru import logger

from app.config.settings import settings


class RedistributionEngine:
    """
    Redistribution AI Engine.

    Pipeline:
    Spatial Occupancy Score
        ↓
    Density Classification
        ↓
    Redistribution Analysis
        ↓
    Find Best Target Carriage
        ↓
    Recommendation
    """

    def __init__(self):
        self.enabled = settings.REDISTRIBUTION_ENABLED
        self.min_diff = settings.REDISTRIBUTION_MIN_DIFF

    def analyze(self, all_car_data: List[Dict], current_car_id: int = None) -> Optional[Dict]:
        """
        Analyze occupancy across all cars and find redistribution opportunities.

        Args:
            all_car_data: List of Dict with car_id, occupancy_ratio, density_indicator
            current_car_id: Optional current car to focus on

        Returns:
            Dict with redistribution recommendation or None
        """
        if not self.enabled or not all_car_data:
            return None

        # Sort cars by occupancy ratio (ascending = least full first)
        sorted_cars = sorted(all_car_data, key=lambda c: c.get("occupancy_ratio", 0))

        if current_car_id:
            # Find current car
            current_car = next((c for c in all_car_data if c.get("car_id") == current_car_id), None)
            if not current_car:
                return None

            current_occupancy = current_car.get("occupancy_ratio", 0)
            current_density = current_car.get("density_indicator", "GREEN")

            # Only recommend if current car is RED or YELLOW
            if current_density not in ("RED", "YELLOW"):
                return None

            # Find best target (lowest occupancy that meets threshold)
            target_car = None
            for car in sorted_cars:
                if car.get("car_id") == current_car_id:
                    continue
                target_occupancy = car.get("occupancy_ratio", 0)
                if current_occupancy - target_occupancy >= self.min_diff:
                    target_car = car
                    break

            if not target_car:
                return None

            return self._create_recommendation(
                current_car, target_car, current_occupancy, target_occupancy
            )

        else:
            # Global redistribution analysis
            return self._global_analysis(sorted_cars)

    def _create_recommendation(
        self,
        source_car: Dict,
        target_car: Dict,
        source_occupancy: float,
        target_occupancy: float,
    ) -> Dict:
        """Create redistribution recommendation."""
        diff = source_occupancy - target_occupancy
        confidence = min(0.95, diff / 1.0)  # Higher difference = higher confidence

        return {
            "action": "REDISTRIBUTION",
            "from_car_id": source_car.get("car_id"),
            "to_car_id": target_car.get("car_id"),
            "from_occupancy": round(float(source_occupancy), 4),
            "to_occupancy": round(float(target_occupancy), 4),
            "occupancy_diff": round(float(diff), 4),
            "confidence": round(float(confidence), 4),
            "reason": f"Car {source_car.get('car_id')} ({source_occupancy:.0%}) is more occupied than Car {target_car.get('car_id')} ({target_occupancy:.0%})",
        }

    def _global_analysis(self, sorted_cars: List[Dict]) -> Optional[Dict]:
        """Perform global redistribution analysis."""
        if len(sorted_cars) < 2:
            return None

        most_occupied = sorted_cars[-1]
        least_occupied = sorted_cars[0]

        most_occ = most_occupied.get("occupancy_ratio", 0)
        least_occ = least_occupied.get("occupancy_ratio", 0)
        diff = most_occ - least_occ

        # Only recommend if significant imbalance
        if diff >= self.min_diff and most_occ > 0.6:
            return {
                "action": "GLOBAL_REDISTRIBUTION",
                "most_occupied_car": most_occupied.get("car_id"),
                "least_occupied_car": least_occupied.get("car_id"),
                "most_occupancy": round(float(most_occ), 4),
                "least_occupancy": round(float(least_occ), 4),
                "imbalance": round(float(diff), 4),
                "confidence": round(min(0.95, diff / 1.0), 4),
                "reason": f"Significant imbalance detected: Car {most_occupied.get('car_id')} ({most_occ:.0%}) vs Car {least_occupied.get('car_id')} ({least_occ:.0%})",
            }

        return None
