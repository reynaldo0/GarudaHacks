import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Application settings loaded from .env file.
    """

    APP_NAME: str = "PROJECT THEMIS"
    APP_VERSION: str = "5.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/themis"

    MODEL_PATH: str = "weights/yolo11s.pt"
    MODEL_CONFIDENCE: float = 0.5
    MODEL_IMAGE_SIZE: int = 640

    YOLO_CLASSES: str = "0"
    PERSON_CLASS_ID: int = 0

    OCCUPANCY_LOW_THRESHOLD: float = 0.4
    OCCUPANCY_NORMAL_THRESHOLD: float = 0.7
    OCCUPANCY_HIGH_THRESHOLD: float = 0.9
    OCCUPANCY_FULL_THRESHOLD: float = 1.0

    # --- Train Configuration ---
    DEFAULT_TRAIN_FORMATION: str = "SF10"
    DEFAULT_CAPACITY: int = 200

    # --- Camera ---
    CAMERA_FPS: int = 1
    CAMERA_RESOLUTION_WIDTH: int = 640
    CAMERA_RESOLUTION_HEIGHT: int = 480

    # --- WebSocket ---
    WS_PATH: str = "/ws"
    WS_HEARTBEAT: int = 30

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/themis.log"

    # --- CORS ---
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000", "http://localhost:5173"]

    @property
    def yolo_classes_list(self) -> List[int]:
        """Parse YOLO_CLASSES string to list of int."""
        try:
            return [int(c.strip()) for c in self.YOLO_CLASSES.split(",")]
        except (ValueError, TypeError):
            return [0]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
