"""
PROJECT THEMIS - State Manager
Version: 6.0

Centralized state management for the entire system.
Maintains real-time state of all trains, cars, cameras, and decisions.
Thread-safe singleton pattern.
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from app.schemas.occupancy import CarSpatialOccupancy, TrainState, Warning, Decision


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
        self._pipeline_states: Dict[str, Dict] = {}
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
            self._pipeline_states.clear()
            self._system_start_time = time.time()

    # --- Train State ---
    def update_car_spatial_occupancy(
        self,
        train_id: str,
        car_id: int,
        occupancy_ratio: float,
        free_space_ratio: float,
        spatial_occupancy_score: float,
        density_indicator: str,
        camera_id: str = None,
    ) -> CarSpatialOccupancy:
        """Update spatial occupancy for a specific car."""
        with self._data_lock:
            if train_id not in self._trains:
                total_cars = 10 if "SF10" in train_id else 8
                self._trains[train_id] = TrainState(
                    train_id=train_id,
                    total_cars=total_cars,
                )

            train = self._trains[train_id]

            risk_score = self._calculate_risk(occupancy_ratio)

            car = CarSpatialOccupancy(
                car_id=car_id,
                occupancy_ratio=round(occupancy_ratio, 4),
                free_space_ratio=round(free_space_ratio, 4),
                density_indicator=density_indicator,
                spatial_occupancy_score=round(spatial_occupancy_score, 4),
                camera_id=camera_id,
                timestamp=datetime.utcnow(),
            )
            car.risk_score = round(risk_score, 4)

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

    def update_pipeline_state(self, train_id: str, car_id: str, pipeline_state: Dict):
        """Update pipeline state for a car."""
        with self._data_lock:
            key = f"{train_id}_{car_id}"
            self._pipeline_states[key] = pipeline_state

    def get_pipeline_state(self, train_id: str, car_id: str) -> Optional[Dict]:
        """Get pipeline state for a car."""
        with self._data_lock:
            key = f"{train_id}_{car_id}"
            return self._pipeline_states.get(key)

    def get_all_pipeline_states(self, train_id: str) -> List[Dict]:
        """Get all pipeline states for a train."""
        with self._data_lock:
            prefix = f"{train_id}_"
            return [
                v for k, v in self._pipeline_states.items()
                if k.startswith(prefix)
            ]

    def get_train_state(self, train_id: str) -> Optional[TrainState]:
        """Get current state of a train."""
        with self._data_lock:
            return self._trains.get(train_id)

    def get_all_trains(self) -> List[TrainState]:
        """Get all train states."""
        with self._data_lock:
            return list(self._trains.values())

    # --- Warnings ---
    def _check_warnings(self, train_id: str, car: CarSpatialOccupancy):
        """Check and create warnings based on density indicator."""
        if car.density_indicator == "RED":
            warning = Warning(
                train_id=train_id,
                car_id=car.car_id,
                warning_type="RED_DENSITY",
                severity="CRITICAL",
                message=f"Car {car.car_id} is RED density (occupancy: {car.occupancy_ratio:.1%})",
                timestamp=datetime.utcnow(),
                is_active=True,
            )
            self._warnings.append(warning)
        elif car.density_indicator == "YELLOW":
            warning = Warning(
                train_id=train_id,
                car_id=car.car_id,
                warning_type="YELLOW_DENSITY",
                severity="WARNING",
                message=f"Car {car.car_id} is YELLOW density (occupancy: {car.occupancy_ratio:.1%})",
                timestamp=datetime.utcnow(),
                is_active=True,
            )
            self._warnings.append(warning)

    def get_active_warnings(self, train_id: str = None) -> List[Warning]:
        """Get active warnings, optionally filtered by train."""
        with self._data_lock:
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
        with self._data_lock:
            train_decisions = [d for d in self._decisions if d.train_id == train_id]
            return train_decisions[-1] if train_decisions else None

    # --- Camera Status ---
    def update_camera_status(self, camera_id: str, status: dict):
        """Update camera status."""
        self._camera_status[camera_id] = status

    def get_camera_status(self, camera_id: str) -> Optional[dict]:
        """Get camera status."""
        with self._data_lock:
            return self._camera_status.get(camera_id)

    # --- Helpers ---
    @staticmethod
    def _calculate_risk(occupancy_ratio: float) -> float:
        if occupancy_ratio < 0.4:
            return 0.1
        elif occupancy_ratio < 0.7:
            return 0.4
        elif occupancy_ratio < 0.9:
            return 0.7
        else:
            return 1.0

    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        with self._data_lock:
            return time.time() - self._system_start_time

    def get_system_summary(self) -> dict:
        """Get a summary of the system state."""
        with self._data_lock:
            return {
                "trains": len(self._trains),
                "activeWarnings": len([w for w in self._warnings if w.is_active]),
                "totalDecisions": len(self._decisions),
                "activeCameras": len(self._camera_status),
                "uptimeSeconds": round(time.time() - self._system_start_time, 2),
            }


state_manager = StateManager()
