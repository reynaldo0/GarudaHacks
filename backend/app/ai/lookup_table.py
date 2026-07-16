"""
PROJECT THEMIS - Lookup Table
Version: 5.0

Camera to train car mapping configuration.
"""

from typing import Dict, Optional
from loguru import logger


# Default camera to car mapping for SF10 formation (20 cameras, 2 per car)
DEFAULT_LOOKUP_TABLE = {
    # Car 1
    "car01_cam01": {"zone": "car_1", "car_id": 1, "type": "cabin"},
    "car01_cam02": {"zone": "car_1", "car_id": 1, "type": "cabin"},
    # Car 2
    "car02_cam01": {"zone": "car_2", "car_id": 2, "type": "cabin"},
    "car02_cam02": {"zone": "car_2", "car_id": 2, "type": "cabin"},
    # Car 3
    "car03_cam01": {"zone": "car_3", "car_id": 3, "type": "cabin"},
    "car03_cam02": {"zone": "car_3", "car_id": 3, "type": "cabin"},
    # Car 4
    "car04_cam01": {"zone": "car_4", "car_id": 4, "type": "cabin"},
    "car04_cam02": {"zone": "car_4", "car_id": 4, "type": "cabin"},
    # Car 5
    "car05_cam01": {"zone": "car_5", "car_id": 5, "type": "cabin"},
    "car05_cam02": {"zone": "car_5", "car_id": 5, "type": "cabin"},
    # Car 6
    "car06_cam01": {"zone": "car_6", "car_id": 6, "type": "cabin"},
    "car06_cam02": {"zone": "car_6", "car_id": 6, "type": "cabin"},
    # Car 7
    "car07_cam01": {"zone": "car_7", "car_id": 7, "type": "cabin"},
    "car07_cam02": {"zone": "car_7", "car_id": 7, "type": "cabin"},
    # Car 8
    "car08_cam01": {"zone": "car_8", "car_id": 8, "type": "cabin"},
    "car08_cam02": {"zone": "car_8", "car_id": 8, "type": "cabin"},
    # Car 9
    "car09_cam01": {"zone": "car_9", "car_id": 9, "type": "cabin"},
    "car09_cam02": {"zone": "car_9", "car_id": 9, "type": "cabin"},
    # Car 10
    "car10_cam01": {"zone": "car_10", "car_id": 10, "type": "cabin"},
    "car10_cam02": {"zone": "car_10", "car_id": 10, "type": "cabin"},
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
