"""
PROJECT THEMIS - State Manager
Version: 5.0

Centralized state management for the entire system.
Maintains real-time state of all trains, cars, cameras, and decisions.
Thread-safe singleton pattern.
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from app.schemas.occupancy import CarOccupancy, TrainState, Warning, Decision


class StateManager:
    """
    Centralized state manager - Single Source of Truth.
    Thread-safe singleton pattern.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._data_lock = threading.RLock()
        self._trains: Dict[str, TrainState] = {}
        self._warnings: List[Warning] = []
        self._decisions: List[Decision] = []
        self._camera_status: Dict[str, dict] = {}
        self._system_start_time = time.time()
        self._initialized = True
        logger.info("StateManager initialized")

    def reset(self):
        """Reset all state (for testing)."""
        with self._data_lock:
            self._trains.clear()
            self._warnings.clear()
            self._decisions.clear()
            self._camera_status.clear()
            self._system_start_time = time.time()

    # --- Train State ---
    def update_car_occupancy(
        self,
        train_id: str,
        car_id: int,
        detected_persons: int,
        capacity: int = 200,
        camera_id: str = None,
    ) -> CarOccupancy:
        """Update occupancy for a specific car."""
        with self._data_lock:
            if train_id not in self._trains:
                total_cars = 10 if "SF10" in train_id else 8
                self._trains[train_id] = TrainState(
                    train_id=train_id,
                    total_cars=total_cars,
                )

            train = self._trains[train_id]
            occupancy_pct = (detected_persons / capacity * 100) if capacity > 0 else 0

            status = self._calculate_status(occupancy_pct)
            risk_score = self._calculate_risk(occupancy_pct)

            car = CarOccupancy(
                car_id=car_id,
                detected_persons=detected_persons,
                capacity=capacity,
                occupancy_percentage=round(occupancy_pct, 2),
                status=status,
                risk_score=round(risk_score, 2),
                timestamp=datetime.utcnow(),
            )

            # Update or append car
            existing_idx = next(
                (i for i, c in enumerate(train.cars) if c.car_id == car_id), None
            )
            if existing_idx is not None:
                train.cars[existing_idx] = car
            else:
                train.cars.append(car)

            train.timestamp = datetime.utcnow()

            # Check warnings
            self._check_warnings(train_id, car)

            return car

    def get_train_state(self, train_id: str) -> Optional[TrainState]:
        """Get current state of a train."""
        return self._trains.get(train_id)

    def get_all_trains(self) -> List[TrainState]:
        """Get all train states."""
        return list(self._trains.values())

    # --- Warnings ---
    def _check_warnings(self, train_id: str, car: CarOccupancy):
        """Check and create warnings based on occupancy."""
        if car.status in ("HIGH", "FULL", "OVERCAPACITY"):
            severity = "CRITICAL" if car.status in ("FULL", "OVERCAPACITY") else "WARNING"
            warning = Warning(
                train_id=train_id,
                car_id=car.car_id,
                warning_type=f"{car.status}_OCCUPANCY",
                severity=severity,
                message=f"Car {car.car_id} is {car.status} ({car.occupancy_percentage}%)",
                timestamp=datetime.utcnow(),
                is_active=True,
            )
            self._warnings.append(warning)

    def get_active_warnings(self, train_id: str = None) -> List[Warning]:
        """Get active warnings, optionally filtered by train."""
        warnings = [w for w in self._warnings if w.is_active]
        if train_id:
            warnings = [w for w in warnings if w.train_id == train_id]
        return warnings

    def clear_old_warnings(self, max_age_seconds: int = 300):
        """Clear warnings older than max_age_seconds."""
        cutoff = datetime.utcnow().timestamp() - max_age_seconds
        for w in self._warnings:
            if w.timestamp.timestamp() < cutoff:
                w.is_active = False

    # --- Decisions ---
    def add_decision(self, decision: Decision):
        """Add a decision to history."""
        self._decisions.append(decision)

    def get_last_decision(self, train_id: str) -> Optional[Decision]:
        """Get the most recent decision for a train."""
        train_decisions = [d for d in self._decisions if d.train_id == train_id]
        return train_decisions[-1] if train_decisions else None

    # --- Camera Status ---
    def update_camera_status(self, camera_id: str, status: dict):
        """Update camera status."""
        self._camera_status[camera_id] = status

    def get_camera_status(self, camera_id: str) -> Optional[dict]:
        """Get camera status."""
        return self._camera_status.get(camera_id)

    # --- Helpers ---
    @staticmethod
    def _calculate_status(occupancy_pct: float) -> str:
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

    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._system_start_time

    def get_system_summary(self) -> dict:
        """Get a summary of the system state."""
        return {
            "trains": len(self._trains),
            "active_warnings": len(self.get_active_warnings()),
            "total_decisions": len(self._decisions),
            "active_cameras": len(self._camera_status),
            "uptime_seconds": round(self.get_uptime(), 2),
        }


state_manager = StateManager()
