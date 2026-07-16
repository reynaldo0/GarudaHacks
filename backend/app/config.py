from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PROJECT THEMIS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./themis.db"

    # WebSocket
    WS_HOST: str = "0.0.0.0"
    WS_PORT: int = 8765

    # YOLO Model
    YOLO_MODEL: str = "yolov11s.pt"
    CONFIDENCE_THRESHOLD: float = 0.5

    # Camera Settings
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    FPS: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
