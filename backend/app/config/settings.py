"""
PROJECT THEMIS - Settings Configuration
Version: 6.0

This module loads all configuration from .env file
and provides them as a single Settings object.
"""

import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from .env file.
    """

    # --- Application ---
    APP_NAME: str = "PROJECT THEMIS"
    APP_VERSION: str = "6.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8005
    WORKERS: int = 1

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/themis"

    # --- AI Model (Spatial Occupancy Segmentation) ---
    SEGMENTATION_MODEL_PATH: str = "weights/segmentation_model.pth"
    SEGMENTATION_CONFIDENCE: float = 0.5
    SEGMENTATION_IMAGE_SIZE: int = 640

    # --- Fisheye Camera Calibration ---
    FISHEYE_CALIBRATION_DIR: str = "config/calibration"
    FISHEYE_K_MATRIX: str = "[]"  # Camera intrinsics matrix (JSON)
    FISHEYE_D_COEFFS: str = "[]"  # Distortion coefficients (JSON)

    # --- Spatial Occupancy Thresholds ---
    DENSITY_GREEN_THRESHOLD: float = 0.6   # free_space > 60% = GREEN
    DENSITY_YELLOW_THRESHOLD: float = 0.3  # free_space 30-60% = YELLOW
    DENSITY_RED_THRESHOLD: float = 0.0     # free_space < 30% = RED

    # --- Train Configuration ---
    DEFAULT_TRAIN_FORMATION: str = "SF6"
    DEFAULT_CAPACITY: int = 200
    FLOOR_AREA_M2: float = 42.0  # Average floor area per car (m^2)

    # --- Camera ---
    NUM_CAMERAS_PER_CAR: int = 4
    CAMERA_TYPE: str = "ceiling_fisheye"
    CAMERA_FPS: int = 1
    CAMERA_RESOLUTION_WIDTH: int = 640
    CAMERA_RESOLUTION_HEIGHT: int = 480
    CAMERA_CAPTURE_INTERVAL: int = 5  # seconds

    # --- Door Automation ---
    DOOR_MIDDLE_OPEN_ON_RED: bool = True  # Auto open middle door when RED

    # --- Redistribution ---
    REDISTRIBUTION_ENABLED: bool = True
    REDISTRIBUTION_MIN_DIFF: float = 0.2  # Min occupancy difference to recommend move

    # --- Bogie Maintenance (CALES) ---
    CALES_HISTORY_SIZE: int = 100  # Number of snapshots to keep per car
    CALES_WHEEL_FLANGE_NOMINAL_MONTHS: int = 12
    CALES_AIR_SPRING_NOMINAL_MONTHS: int = 192
    CALES_CHEVRON_RUBBER_NOMINAL_MONTHS: int = 72

    # --- WebSocket ---
    WS_PATH: str = "/ws"
    WS_HEARTBEAT: int = 30

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/themis.log"

    # --- CORS ---
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    # --- Auth & Security ---
    JWT_SECRET: str = "themis-dev-secret-change-me"
    API_KEY: str = "themis-unity-key-2026"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000", "http://localhost:5173"]

    @property
    def fisheye_k(self) -> list:
        """Parse FISHEYE_K_MATRIX JSON string to list."""
        try:
            return json.loads(self.FISHEYE_K_MATRIX)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def fisheye_d(self) -> list:
        """Parse FISHEYE_D_COEFFS JSON string to list."""
        try:
            return json.loads(self.FISHEYE_D_COEFFS)
        except (json.JSONDecodeError, TypeError):
            return []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
