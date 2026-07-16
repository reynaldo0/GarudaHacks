"""
PROJECT THEMIS - Lookup Table
Version: 6.0

Camera to train car mapping configuration.
4 ceiling fisheye cameras per car.
"""

from typing import Dict, Optional
from loguru import logger


# Default camera to car mapping for SF10 formation (40 cameras, 4 per car)
# Each camera is a ceiling fisheye covering one quadrant of the carriage
DEFAULT_LOOKUP_TABLE = {
    # Car 1
    "car01_cam01": {"zone": "car_1_front_left", "car_id": 1, "type": "ceiling_fisheye", "position": "front_left"},
    "car01_cam02": {"zone": "car_1_front_right", "car_id": 1, "type": "ceiling_fisheye", "position": "front_right"},
    "car01_cam03": {"zone": "car_1_rear_left", "car_id": 1, "type": "ceiling_fisheye", "position": "rear_left"},
    "car01_cam04": {"zone": "car_1_rear_right", "car_id": 1, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 2
    "car02_cam01": {"zone": "car_2_front_left", "car_id": 2, "type": "ceiling_fisheye", "position": "front_left"},
    "car02_cam02": {"zone": "car_2_front_right", "car_id": 2, "type": "ceiling_fisheye", "position": "front_right"},
    "car02_cam03": {"zone": "car_2_rear_left", "car_id": 2, "type": "ceiling_fisheye", "position": "rear_left"},
    "car02_cam04": {"zone": "car_2_rear_right", "car_id": 2, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 3
    "car03_cam01": {"zone": "car_3_front_left", "car_id": 3, "type": "ceiling_fisheye", "position": "front_left"},
    "car03_cam02": {"zone": "car_3_front_right", "car_id": 3, "type": "ceiling_fisheye", "position": "front_right"},
    "car03_cam03": {"zone": "car_3_rear_left", "car_id": 3, "type": "ceiling_fisheye", "position": "rear_left"},
    "car03_cam04": {"zone": "car_3_rear_right", "car_id": 3, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 4
    "car04_cam01": {"zone": "car_4_front_left", "car_id": 4, "type": "ceiling_fisheye", "position": "front_left"},
    "car04_cam02": {"zone": "car_4_front_right", "car_id": 4, "type": "ceiling_fisheye", "position": "front_right"},
    "car04_cam03": {"zone": "car_4_rear_left", "car_id": 4, "type": "ceiling_fisheye", "position": "rear_left"},
    "car04_cam04": {"zone": "car_4_rear_right", "car_id": 4, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 5
    "car05_cam01": {"zone": "car_5_front_left", "car_id": 5, "type": "ceiling_fisheye", "position": "front_left"},
    "car05_cam02": {"zone": "car_5_front_right", "car_id": 5, "type": "ceiling_fisheye", "position": "front_right"},
    "car05_cam03": {"zone": "car_5_rear_left", "car_id": 5, "type": "ceiling_fisheye", "position": "rear_left"},
    "car05_cam04": {"zone": "car_5_rear_right", "car_id": 5, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 6
    "car06_cam01": {"zone": "car_6_front_left", "car_id": 6, "type": "ceiling_fisheye", "position": "front_left"},
    "car06_cam02": {"zone": "car_6_front_right", "car_id": 6, "type": "ceiling_fisheye", "position": "front_right"},
    "car06_cam03": {"zone": "car_6_rear_left", "car_id": 6, "type": "ceiling_fisheye", "position": "rear_left"},
    "car06_cam04": {"zone": "car_6_rear_right", "car_id": 6, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 7
    "car07_cam01": {"zone": "car_7_front_left", "car_id": 7, "type": "ceiling_fisheye", "position": "front_left"},
    "car07_cam02": {"zone": "car_7_front_right", "car_id": 7, "type": "ceiling_fisheye", "position": "front_right"},
    "car07_cam03": {"zone": "car_7_rear_left", "car_id": 7, "type": "ceiling_fisheye", "position": "rear_left"},
    "car07_cam04": {"zone": "car_7_rear_right", "car_id": 7, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 8
    "car08_cam01": {"zone": "car_8_front_left", "car_id": 8, "type": "ceiling_fisheye", "position": "front_left"},
    "car08_cam02": {"zone": "car_8_front_right", "car_id": 8, "type": "ceiling_fisheye", "position": "front_right"},
    "car08_cam03": {"zone": "car_8_rear_left", "car_id": 8, "type": "ceiling_fisheye", "position": "rear_left"},
    "car08_cam04": {"zone": "car_8_rear_right", "car_id": 8, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 9
    "car09_cam01": {"zone": "car_9_front_left", "car_id": 9, "type": "ceiling_fisheye", "position": "front_left"},
    "car09_cam02": {"zone": "car_9_front_right", "car_id": 9, "type": "ceiling_fisheye", "position": "front_right"},
    "car09_cam03": {"zone": "car_9_rear_left", "car_id": 9, "type": "ceiling_fisheye", "position": "rear_left"},
    "car09_cam04": {"zone": "car_9_rear_right", "car_id": 9, "type": "ceiling_fisheye", "position": "rear_right"},
    # Car 10
    "car10_cam01": {"zone": "car_10_front_left", "car_id": 10, "type": "ceiling_fisheye", "position": "front_left"},
    "car10_cam02": {"zone": "car_10_front_right", "car_id": 10, "type": "ceiling_fisheye", "position": "front_right"},
    "car10_cam03": {"zone": "car_10_rear_left", "car_id": 10, "type": "ceiling_fisheye", "position": "rear_left"},
    "car10_cam04": {"zone": "car_10_rear_right", "car_id": 10, "type": "ceiling_fisheye", "position": "rear_right"},
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
        """Get camera type (ceiling_fisheye) from camera ID."""
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

    def get_position(self, camera_id: str) -> Optional[str]:
        """Get camera position (front_left, front_right, rear_left, rear_right) from camera ID."""
        entry = self._table.get(camera_id)
        if entry:
            return entry["position"]
        return None

    def get_cameras_for_car(self, car_id: int) -> list:
        """Get all camera IDs mapped to a car."""
        return [
            cam_id
            for cam_id, entry in self._table.items()
            if entry["car_id"] == car_id
        ]

    def get_total_cameras(self) -> int:
        """Get total number of cameras."""
        return len(self._table)

    def get_total_cars(self) -> int:
        """Get total number of cars."""
        return max(entry["car_id"] for entry in self._table.values())

    def get_all_mappings(self) -> Dict:
        """Get full lookup table."""
        return self._table.copy()
