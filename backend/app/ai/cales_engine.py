"""
PROJECT THEMIS - CALES Engine
Version: 5.0

Computer-Aided Logistics and Evaluation System.
Predicts future occupancy and generates recommendations.
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class CALESEngine:
    """Prediction and recommendation engine."""

    def __init__(self):
        self._history: Dict[int, List[Dict]] = {}  # car_id -> list of occupancy snapshots

    def add_snapshot(self, car_id: int, occupancy_pct: float, person_count: int):
        """Add occupancy snapshot to history."""
        if car_id not in self._history:
            self._history[car_id] = []

        self._history[car_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "occupancy_pct": occupancy_pct,
            "person_count": person_count,
        })

        # Keep last 100 snapshots
        if len(self._history[car_id]) > 100:
            self._history[car_id] = self._history[car_id][-100:]

    def predict(self, car_id: int, horizon_minutes: int = 15) -> Dict:
        """Predict future occupancy for a car."""
        history = self._history.get(car_id, [])
        if not history:
            return {
                "predicted_occupancy": 0,
                "risk_score": 0,
                "confidence": 0,
            }

        # Simple linear prediction based on recent trend
        recent = history[-5:] if len(history) >= 5 else history
        if len(recent) < 2:
            return {
                "predicted_occupancy": recent[-1]["occupancy_pct"],
                "risk_score": 0,
                "confidence": 0.5,
            }

        # Calculate trend
        first = recent[0]["occupancy_pct"]
        last = recent[-1]["occupancy_pct"]
        trend = (last - first) / len(recent)

        predicted = last + (trend * horizon_minutes)
        predicted = max(0, min(150, predicted))  # Clamp

        risk = self._calculate_risk(predicted)

        return {
            "predicted_occupancy": round(predicted, 2),
            "risk_score": round(risk, 2),
            "confidence": 0.7,
            "horizon_minutes": horizon_minutes,
        }

    def generate_recommendation(self, cars: List[Dict]) -> Optional[Dict]:
        """
        Generate recommendation based on all car occupancy.
        Returns move recommendation if imbalance detected.
        """
        if not cars:
            return None

        # Find most full and least full cars
        sorted_cars = sorted(cars, key=lambda c: c.get("occupancy_percentage", 0), reverse=True)

        most_full = sorted_cars[0]
        least_full = sorted_cars[-1]

        full_occ = most_full.get("occupancy_percentage", 0)
        empty_occ = least_full.get("occupancy_percentage", 0)

        # Only recommend if significant imbalance
        if full_occ - empty_occ > 30 and full_occ > 70:
            return {
                "action": "MOVE_PASSENGER",
                "from_car_id": most_full.get("car_id"),
                "to_car_id": least_full.get("car_id"),
                "confidence": round(min(0.95, (full_occ - empty_occ) / 100), 2),
                "reason": f"Car {most_full.get('car_id')} is {full_occ}% full. Car {least_full.get('car_id')} is only {empty_occ}% full.",
            }

        return None

    @staticmethod
    def _calculate_risk(occupancy_pct: float) -> float:
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
