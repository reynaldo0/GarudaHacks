"""
PROJECT THEMIS - CCALES Engine
Version: 6.0

Cumulative Asymmetric Load Exposure Score.
Measures bogie health based on spatial occupancy patterns.
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from app.config.settings import settings


class CCALESEngine:
    """
    CCALES Engine for Bogie Predictive Maintenance.

    Pipeline:
    Spatial Occupancy Score
        ↓
    CALES Score
        ↓
    Health Index
        ↓
    Damage Multiplier
        ↓
    RUL (Remaining Useful Life)
        ↓
    OPEX Estimation
        ↓
    Inspection Priority
    """

    def __init__(self):
        self._history: Dict[int, List[Dict]] = {}  # car_id -> list of snapshots
        self.max_history = settings.CALES_HISTORY_SIZE

        # Nominal life in months
        self.wheel_flange_nominal = settings.CALES_WHEEL_FLANGE_NOMINAL_MONTHS
        self.air_spring_nominal = settings.CALES_AIR_SPRING_NOMINAL_MONTHS
        self.chevron_rubber_nominal = settings.CALES_CHEVRON_RUBBER_NOMINAL_MONTHS

    def add_snapshot(self, car_id: int, spatial_occupancy_score: float, occupancy_ratio: float):
        """Add spatial occupancy snapshot to history."""
        if car_id not in self._history:
            self._history[car_id] = []

        self._history[car_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "spatial_occupancy_score": spatial_occupancy_score,
            "occupancy_ratio": occupancy_ratio,
        })

        # Keep last N snapshots
        if len(self._history[car_id]) > self.max_history:
            self._history[car_id] = self._history[car_id][-self.max_history:]

    def calculate_cales_score(self, car_id: int, all_car_occupancies: List[Dict]) -> Dict:
        """
        Calculate CALES score for a specific car.

        CALES measures:
        - Level of load
        - Asymmetry of load (compared to average)
        - Duration of load

        Returns:
            Dict with cales_score, status, health_index, damage_multiplier
        """
        history = self._history.get(car_id, [])

        if not history:
            return self._default_cales()

        # Get current occupancy
        current = history[-1]
        current_score = current["spatial_occupancy_score"]

        # Calculate average occupancy across all cars
        avg_score = self._calculate_average_score(all_car_occupancies)

        # Asymmetry ratio
        asymmetry_ratio = current_score / avg_score if avg_score > 0 else 1.0

        # Severity weight (higher asymmetry = higher severity)
        severity_weight = self._calculate_severity_weight(asymmetry_ratio)

        # Duration factor (longer overload = higher score)
        duration_factor = self._calculate_duration_factor(history)

        # Calculate CALES score (0.0 - 1.0)
        cales_score = min(1.0, current_score * severity_weight * duration_factor)

        # Determine CALES status
        status = self._determine_cales_status(cales_score)

        # Calculate health index (100% = perfect, 0% = critical)
        health_index = max(0, 100 - (cales_score * 100))

        # Calculate damage multiplier
        damage_multiplier = self._get_damage_multiplier(status)

        return {
            "car_id": car_id,
            "cales_score": round(float(cales_score), 4),
            "status": status,
            "health_index": round(float(health_index), 2),
            "damage_multiplier": round(float(damage_multiplier), 2),
            "asymmetry_ratio": round(float(asymmetry_ratio), 4),
            "severity_weight": round(float(severity_weight), 4),
            "duration_factor": round(float(duration_factor), 4),
        }

    def calculate_rul(self, car_id: int, cales_score: float) -> Dict:
        """
        Calculate Remaining Useful Life for bogie components.

        Returns:
            Dict with RUL for each component in months
        """
        # Damage multiplier based on CALES score
        damage_mult = 1.0 + (cales_score * 2.0)  # 1.0x to 3.0x

        wheel_flange_effective = self.wheel_flange_nominal / damage_mult
        air_spring_effective = self.air_spring_nominal / damage_mult
        chevron_rubber_effective = self.chevron_rubber_nominal / damage_mult

        return {
            "wheel_flange_rul": round(float(wheel_flange_effective), 1),
            "air_spring_rul": round(float(air_spring_effective), 1),
            "chevron_rubber_rul": round(float(chevron_rubber_effective), 1),
            "damage_multiplier": round(float(damage_mult), 2),
        }

    def estimate_opex(self, status: str, cales_score: float) -> Dict:
        """
        Estimate operational expenditure if inspection is delayed.

        Returns:
            Dict with estimated costs
        """
        base_costs = {
            "GREEN": {"wheel_reprofile": 15_000_000, "air_spring_overhaul": 0, "catastrophic_risk": 0},
            "YELLOW": {"wheel_reprofile": 20_000_000, "air_spring_overhaul": 0, "catastrophic_risk": 500_000_000},
            "ORANGE": {"wheel_reprofile": 25_000_000, "air_spring_overhaul": 150_000_000, "catastrophic_risk": 1_000_000_000},
            "RED": {"wheel_reprofile": 25_000_000, "air_spring_overhaul": 150_000_000, "catastrophic_risk": 2_000_000_000},
        }

        costs = base_costs.get(status, base_costs["GREEN"])

        # Scale by CALES score
        scale = 1.0 + cales_score
        return {
            "wheel_reprofile_est": int(costs["wheel_reprofile"] * scale),
            "air_spring_overhaul_est": int(costs["air_spring_overhaul"] * scale),
            "catastrophic_risk_est": int(costs["catastrophic_risk"] * scale),
            "total_potential_cost": int(sum(costs.values()) * scale),
        }

    def determine_inspection_priority(self, all_car_cales: List[Dict]) -> List[Dict]:
        """
        Determine inspection priority for all cars.

        Returns:
            List of dicts sorted by priority (highest CALES score = highest priority)
        """
        # Sort by CALES score (descending)
        sorted_cars = sorted(all_car_cales, key=lambda c: c.get("cales_score", 0), reverse=True)

        priorities = []
        for i, car in enumerate(sorted_cars):
            priorities.append({
                "priority_rank": i + 1,
                "car_id": car.get("car_id"),
                "cales_score": car.get("cales_score"),
                "status": car.get("status"),
                "health_index": car.get("health_index"),
                "recommended_action": self._get_recommended_action(car.get("status")),
            })

        return priorities

    def _calculate_average_score(self, all_car_occupancies: List[Dict]) -> float:
        """Calculate average spatial occupancy score across all cars."""
        if not all_car_occupancies:
            return 0.5  # Default average

        scores = [c.get("spatial_occupancy_score", 0.5) for c in all_car_occupancies]
        return sum(scores) / len(scores) if scores else 0.5

    def _calculate_severity_weight(self, asymmetry_ratio: float) -> float:
        """Calculate severity weight from asymmetry ratio."""
        if asymmetry_ratio <= 1.0:
            return 1.0
        elif asymmetry_ratio <= 1.5:
            return 1.5
        elif asymmetry_ratio <= 2.0:
            return 2.0
        else:
            return 3.0

    def _calculate_duration_factor(self, history: List[Dict]) -> float:
        """Calculate duration factor from history."""
        if len(history) < 2:
            return 1.0

        # Check how many recent snapshots are above threshold
        recent = history[-10:] if len(history) >= 10 else history
        high_load_count = sum(1 for s in recent if s["spatial_occupancy_score"] > 0.7)

        # More high-load snapshots = higher duration factor
        return 1.0 + (high_load_count * 0.1)

    def _determine_cales_status(self, cales_score: float) -> str:
        """Determine CALES status from score."""
        if cales_score < 0.3:
            return "GREEN"
        elif cales_score < 0.5:
            return "YELLOW"
        elif cales_score < 0.7:
            return "ORANGE"
        else:
            return "RED"

    def _get_damage_multiplier(self, status: str) -> float:
        """Get damage multiplier from CALES status."""
        multipliers = {
            "GREEN": 1.0,
            "YELLOW": 1.0,
            "ORANGE": 2.5,
            "RED": 3.0,
        }
        return multipliers.get(status, 1.0)

    def _get_recommended_action(self, status: str) -> str:
        """Get recommended action from CALES status."""
        actions = {
            "GREEN": "CONTINUE_MONITORING",
            "YELLOW": "SCHEDULE_INSPECTION",
            "ORANGE": "PRIORITY_INSPECTION",
            "RED": "IMMEDIATE_DEPOT_INSPECTION",
        }
        return actions.get(status, "CONTINUE_MONITORING")

    def _default_cales(self) -> Dict:
        """Return default CALES values."""
        return {
            "car_id": 0,
            "cales_score": 0.0,
            "status": "GREEN",
            "health_index": 100.0,
            "damage_multiplier": 1.0,
            "asymmetry_ratio": 1.0,
            "severity_weight": 1.0,
            "duration_factor": 1.0,
        }
