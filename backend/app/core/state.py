from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class SystemState:
    occupancy: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
    warning: str = ""
    prediction: Dict[str, Any] = field(default_factory=dict)
    train_state: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class StateManager:
    _instance: Optional["StateManager"] = None
    _state: SystemState = SystemState()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_state(self) -> Dict[str, Any]:
        return {
            "occupancy": self._state.occupancy,
            "recommendation": self._state.recommendation,
            "warning": self._state.warning,
            "prediction": self._state.prediction,
            "train_state": self._state.train_state,
            "last_updated": self._state.last_updated.isoformat(),
        }

    def update_occupancy(self, data: Dict[str, Any]):
        self._state.occupancy = data
        self._state.last_updated = datetime.now()

    def update_recommendation(self, recommendation: str):
        self._state.recommendation = recommendation
        self._state.last_updated = datetime.now()

    def update_warning(self, warning: str):
        self._state.warning = warning
        self._state.last_updated = datetime.now()


state_manager = StateManager()
