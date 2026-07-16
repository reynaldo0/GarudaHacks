"""
PROJECT THEMIS - Occupancy Grid Engine
Version: 6.0

Generates and fuses occupancy grids from multiple fisheye cameras.
"""

import numpy as np
from typing import Dict, List, Optional
from loguru import logger


class OccupancyGridEngine:
    """
    Generates occupancy grids from spatial segmentation results.
    Each of 4 fisheye cameras generates its own occupancy grid.
    These are fused into a single carriage occupancy map.
    """

    def __init__(self, grid_size: int = 64):
        self.grid_size = grid_size

    def generate_grid(self, segmentation_result: Dict) -> np.ndarray:
        """
        Generate occupancy grid from segmentation result.

        Args:
            segmentation_result: Dict with 'occupancy_grid' (NxM np.ndarray)

        Returns:
            np.ndarray: Normalized occupancy grid (0.0 = free, 1.0 = occupied)
        """
        if segmentation_result is None:
            return np.zeros((self.grid_size, self.grid_size), dtype=np.float32)

        grid = segmentation_result.get("occupancy_grid", None)
        if grid is None:
            return np.zeros((self.grid_size, self.grid_size), dtype=np.float32)

        # Ensure correct size
        if grid.shape != (self.grid_size, self.grid_size):
            grid = self._resize_grid(grid, self.grid_size)

        # Normalize to 0.0 - 1.0
        if grid.max() > 1.0:
            grid = grid.astype(np.float32) / 255.0

        return grid

    def fuse_grids(self, grids: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Fuse multiple occupancy grids into a single carriage occupancy map.

        Args:
            grids: List of occupancy grids from 4 cameras
            weights: Optional weights for each camera (front cameras weighted higher)

        Returns:
            np.ndarray: Fused occupancy grid
        """
        if not grids:
            return np.zeros((self.grid_size, self.grid_size), dtype=np.float32)

        if weights is None:
            weights = [1.0] * len(grids)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(grids)] * len(grids)

        # Weighted sum
        fused = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        for grid, weight in zip(grids, weights):
            resized = self._resize_grid(grid, self.grid_size) if grid.shape != (self.grid_size, self.grid_size) else grid
            fused += resized.astype(np.float32) * weight

        # Clip to valid range
        fused = np.clip(fused, 0.0, 1.0)

        return fused

    def calculate_occupancy_metrics(self, fused_grid: np.ndarray) -> Dict:
        """
        Calculate occupancy metrics from fused grid.

        Returns:
            Dict with:
                - occupancy_ratio: float (0.0 - 1.0)
                - free_space_ratio: float (0.0 - 1.0)
                - spatial_occupancy_score: float
                - grid_density: float (average occupancy per cell)
        """
        total_cells = fused_grid.size
        occupied_cells = np.sum(fused_grid > 0.5)  # Threshold at 0.5
        free_cells = total_cells - occupied_cells

        occupancy_ratio = occupied_cells / total_cells if total_cells > 0 else 0.0
        free_space_ratio = free_cells / total_cells if total_cells > 0 else 1.0
        spatial_occupancy_score = float(np.mean(fused_grid))
        grid_density = float(np.mean(fused_grid > 0.5))

        return {
            "occupancy_ratio": round(float(occupancy_ratio), 4),
            "free_space_ratio": round(float(free_space_ratio), 4),
            "spatial_occupancy_score": round(float(spatial_occupancy_score), 4),
            "grid_density": round(float(grid_density), 4),
        }

    def _resize_grid(self, grid: np.ndarray, target_size: int) -> np.ndarray:
        """Resize grid to target size using interpolation."""
        import cv2
        resized = cv2.resize(grid.astype(np.float32), (target_size, target_size), interpolation=cv2.INTER_LINEAR)
        return resized
