"""
PROJECT THEMIS - Pydantic Schemas
Version: 6.0

Request and response schemas for API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Car Spatial Occupancy ---
class CarSpatialOccupancy(BaseModel):
    car_id: int
    occupancy_ratio: float = 0.0         # 0.0 - 1.0
    free_space_ratio: float = 1.0        # 0.0 - 1.0
    density_indicator: str = "GREEN"     # GREEN, YELLOW, RED
    spatial_occupancy_score: float = 0.0 # 0.0 - 1.0
    floor_area_m2: float = 42.0
    camera_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Train State ---
class TrainState(BaseModel):
    train_id: str
    formation: str = "SF10"
    total_cars: int = 10
    cars: List[CarSpatialOccupancy] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Warning ---
class Warning(BaseModel):
    train_id: str
    car_id: int
    warning_type: str
    severity: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


# --- Decision ---
class Decision(BaseModel):
    train_id: str
    from_car_id: int
    to_car_id: Optional[int] = None
    action: str  # REDISTRIBUTION, DOOR_OPEN, DOOR_CLOSE
    door_action: Optional[str] = None  # OPEN_MIDDLE, CLOSE
    announcement: Optional[str] = None
    confidence: float
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Camera Frame ---
class FrameData(BaseModel):
    camera_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    frame_base64: Optional[str] = None
    spatial_occupancy_score: float = 0.0


# --- Pipeline State (Main Response) ---
class PipelineState(BaseModel):
    car_id: str
    occupancy_ratio: float = 0.0
    free_space_ratio: float = 1.0
    density_indicator: str = "GREEN"     # GREEN, YELLOW, RED
    spatial_occupancy_score: float = 0.0
    recommended_target: Optional[str] = None
    door_action: str = "CLOSE"           # OPEN_MIDDLE, CLOSE
    announcement: Optional[str] = None
    cales_score: float = 0.0
    health_index: float = 100.0
    damage_multiplier: float = 1.0
    inspection_priority: int = 0
    recommended_action: str = "CONTINUE_MONITORING"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- API Responses ---
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusResponse(BaseModel):
    status: str
    message: str
    version: str
    uptime: float


class OccupancyResponse(BaseModel):
    train_id: str
    cars: List[CarSpatialOccupancy]
    timestamp: datetime


class PredictionResponse(BaseModel):
    train_id: str
    car_id: int
    predicted_occupancy_ratio: float
    risk_score: float
    confidence: float
    prediction_horizon_minutes: int


class ConfigResponse(BaseModel):
    train_id: str
    formation: str
    total_cars: int
    capacity_per_car: int
    cameras: List[dict] = []
