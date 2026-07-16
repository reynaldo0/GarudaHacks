"""
PROJECT THEMIS - Fusion Engine
Version: 6.0

Merges 4 occupancy grids from 4 ceiling fisheye cameras into single carriage occupancy map.
"""

import numpy as np
from typing import Dict, List, Optional
from loguru import logger

from app.ai.occupancy_grid import OccupancyGridEngine


class FusionEngine:
    """
    Spatial Fusion Engine.

    Merges 4 occupancy grids from 4 fisheye cameras into a single carriage occupancy map.
    No global people tracking. No ReID. No duplicate counting.
    """

    def __init__(self):
        self.grid_engine = OccupancyGridEngine(grid_size=64)
        # Default weights: front cameras weighted slightly higher
        self.default_weights = [1.2, 1.2, 1.0, 1.0]  # front_left, front_right, rear_left, rear_right

    def fuse(self, camera_results: List[Dict], weights: Optional[List[float]] = None) -> Dict:
        """
        Fuse occupancy data from multiple cameras.

        Args:
            camera_results: List of Dict from spatial_engine.predict() for each camera
            weights: Optional weights for each camera

        Returns:
            Dict with fused occupancy metrics
        """
        if not camera_results:
            return self._empty_result()

        if weights is None:
            weights = self.default_weights[:len(camera_results)]

        # Generate occupancy grids
        grids = []
        for result in camera_results:
            grid = self.grid_engine.generate_grid(result)
            grids.append(grid)

        # Fuse grids
        fused_grid = self.grid_engine.fuse_grids(grids, weights)

        # Calculate metrics
        metrics = self.grid_engine.calculate_occupancy_metrics(fused_grid)

        return {
            **metrics,
            "source": "fused",
            "camera_count": len(camera_results),
            "confidence": self._calculate_confidence(camera_results),
        }

    def fuse_from_grids(self, grids: List[np.ndarray], weights: Optional[List[float]] = None) -> Dict:
        """
        Fuse pre-generated occupancy grids directly.

        Args:
            grids: List of np.ndarray occupancy grids
            weights: Optional weights

        Returns:
            Dict with fused occupancy metrics
        """
        if not grids:
            return self._empty_result()

        if weights is None:
            weights = self.default_weights[:len(grids)]

        fused_grid = self.grid_engine.fuse_grids(grids, weights)
        metrics = self.grid_engine.calculate_occupancy_metrics(fused_grid)

        return {
            **metrics,
            "source": "fused_grids",
            "camera_count": len(grids),
            "confidence": 0.85,
        }

    def _calculate_confidence(self, camera_results: List[Dict]) -> float:
        """Calculate confidence based on camera results."""
        if not camera_results:
            return 0.0

        # Average confidence from all cameras
        confidences = [r.get("confidence", 0.0) for r in camera_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Bonus for having multiple cameras
        camera_bonus = min(0.1, len(camera_results) * 0.025)

        return round(min(1.0, avg_confidence + camera_bonus), 4)

    def _empty_result(self) -> Dict:
        """Return empty result when no camera data."""
        return {
            "occupancy_ratio": 0.0,
            "free_space_ratio": 1.0,
            "spatial_occupancy_score": 0.0,
            "grid_density": 0.0,
            "source": "none",
            "camera_count": 0,
            "confidence": 0.0,
        }
