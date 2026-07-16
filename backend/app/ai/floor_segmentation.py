"""
PROJECT THEMIS - Floor Segmentation
Version: 6.0

Floor segmentation using color-based heuristic (for Unity digital twin).
In production, this would use semantic segmentation model.
"""

import cv2
import numpy as np
from typing import Dict, Optional
from loguru import logger


class FloorSegmentation:
    """
    Floor segmentation engine.

    In Unity digital twin, floor color is consistent (#e7d3a9 or similar).
    Uses HSV color range to segment floor from other objects.

    In production, replace with semantic segmentation model (U-Net, Mask R-CNN).
    """

    # HSV range for typical train floor color (#e7d3a9)
    FLOOR_HSV_LOW = np.array([20, 30, 150])
    FLOOR_HSV_HIGH = np.array([35, 80, 255])

    def __init__(self):
        self.grid_size = 64

    def segment(self, frame: np.ndarray) -> Dict:
        """
        Segment floor from frame.

        Args:
            frame: Input BGR frame

        Returns:
            Dict with:
                - floor_mask: np.ndarray (binary mask)
                - floor_ratio: float (0.0 - 1.0, ratio of visible floor)
                - confidence: float
        """
        if frame is None:
            return self._empty_result()

        try:
            # Convert to HSV for color-based segmentation
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create floor mask
            floor_mask = cv2.inRange(hsv, self.FLOOR_HSV_LOW, self.FLOOR_HSV_HIGH)

            # Clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel)
            floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)

            # Calculate floor ratio
            total_pixels = floor_mask.size
            floor_pixels = np.sum(floor_mask > 0)
            floor_ratio = floor_pixels / total_pixels if total_pixels > 0 else 0.0

            # Resize mask to grid size
            grid_mask = cv2.resize(floor_mask, (self.grid_size, self.grid_size))
            grid_binary = (grid_mask > 0).astype(np.uint8)

            return {
                "floor_mask": grid_binary,
                "floor_ratio": round(float(floor_ratio), 4),
                "confidence": 0.8,
            }

        except Exception as e:
            logger.error(f"Floor segmentation error: {e}")
            return self._empty_result()

    def segment_with_visibility_score(self, frame: np.ndarray) -> Dict:
        """
        Segment floor and calculate visibility score.

        Returns:
            Dict with:
                - floor_mask: np.ndarray
                - floor_visibility_score: float (0.0 - 1.0)
                - occupancy_from_floor: float (0.0 - 1.0)
        """
        result = self.segment(frame)

        floor_ratio = result["floor_ratio"]

        # Floor visibility = how much floor is visible
        # High floor visibility = low occupancy
        floor_visibility_score = floor_ratio
        occupancy_from_floor = 1.0 - floor_ratio

        result["floor_visibility_score"] = round(float(floor_visibility_score), 4)
        result["occupancy_from_floor"] = round(float(occupancy_from_floor), 4)

        return result

    def _empty_result(self) -> Dict:
        """Return empty result when frame is invalid."""
        return {
            "floor_mask": np.zeros((self.grid_size, self.grid_size), dtype=np.uint8),
            "floor_ratio": 0.0,
            "floor_visibility_score": 0.0,
            "occupancy_from_floor": 1.0,
            "confidence": 0.0,
        }
