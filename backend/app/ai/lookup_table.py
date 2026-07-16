"""
PROJECT THEMIS - Lookup Table
Version: 5.0

Camera to train car mapping configuration.
"""

from typing import Dict, Optional
from loguru import logger

DEFAULT_LOOKUP_TABLE = {
    # Platform cameras (external view)
    "platform_01": {"zone": "A", "car_id": 1, "type": "platform"},
    "platform_02": {"zone": "B", "car_id": 2, "type": "platform"},
    "platform_03": {"zone": "C", "car_id": 3, "type": "platform"},
    "platform_04": {"zone": "D", "car_id": 4, "type": "platform"},
    "platform_05": {"zone": "E", "car_id": 5, "type": "platform"},
    "platform_06": {"zone": "F", "car_id": 6, "type": "platform"},
    "platform_07": {"zone": "G", "car_id": 7, "type": "platform"},
    "platform_08": {"zone": "H", "car_id": 8, "type": "platform"},
    "platform_09": {"zone": "I", "car_id": 9, "type": "platform"},
    "platform_10": {"zone": "J", "car_id": 10, "type": "platform"},
    # Cabin cameras (internal view)
    "cabin_01": {"zone": "cabin_1", "car_id": 1, "type": "cabin"},
    "cabin_02": {"zone": "cabin_2", "car_id": 2, "type": "cabin"},
    "cabin_03": {"zone": "cabin_3", "car_id": 3, "type": "cabin"},
    "cabin_04": {"zone": "cabin_4", "car_id": 4, "type": "cabin"},
    "cabin_05": {"zone": "cabin_5", "car_id": 5, "type": "cabin"},
    "cabin_06": {"zone": "cabin_6", "car_id": 6, "type": "cabin"},
    "cabin_07": {"zone": "cabin_7", "car_id": 7, "type": "cabin"},
    "cabin_08": {"zone": "cabin_8", "car_id": 8, "type": "cabin"},
    "cabin_09": {"zone": "cabin_9", "car_id": 9, "type": "cabin"},
    "cabin_10": {"zone": "cabin_10", "car_id": 10, "type": "cabin"},
}


class LookupTable:
    """Camera to train car mapping lookup."""

    def __init__(self):
        self._table = DEFAULT_LOOKUP_TABLE.copy()

    def get_car_id(self, camera_id: str) -> Optional[int]:
        """Get car ID from camera ID."""
        entry = self._table.get(camera_id)
        if entry:
            return entry["car_id"]
        return None

    def get_camera_type(self, camera_id: str) -> Optional[str]:
        """Get camera type (platform/cabin) from camera ID."""
        entry = self._table.get(camera_id)
        if entry:
            return entry["type"]
        return None

    def get_zone(self, camera_id: str) -> Optional[str]:
        """Get zone from camera ID."""
        entry = self._table.get(camera_id)
        if entry:
            return entry["zone"]
        return None

    def get_cameras_for_car(self, car_id: int) -> list:
        """Get all camera IDs mapped to a car."""
        return [
            cam_id
            for cam_id, entry in self._table.items()
            if entry["car_id"] == car_id
        ]

    def get_all_mappings(self) -> Dict:
        """Get full lookup table."""
        return self._table.copy()
