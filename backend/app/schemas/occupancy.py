"""
PROJECT THEMIS - Pydantic Schemas
Version: 5.0

Request and response schemas for API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Car Occupancy ---
class CarOccupancy(BaseModel):
    car_id: int
    detected_persons: int = 0
    capacity: int = 200
    occupancy_percentage: float = 0.0
    status: str = "LOW"
    risk_score: float = 0.0
    camera_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Train State ---
class TrainState(BaseModel):
    train_id: str
    formation: str = "SF10"
    total_cars: int = 10
    cars: List[CarOccupancy] = []
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
    to_car_id: int
    action: str
    confidence: float
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Camera Frame ---
class FrameData(BaseModel):
    camera_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    frame_base64: Optional[str] = None
    persons_detected: int = 0


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
    cars: List[CarOccupancy]
    timestamp: datetime


class PredictionResponse(BaseModel):
    train_id: str
    car_id: int
    predicted_occupancy: float
    risk_score: float
    confidence: float
    prediction_horizon_minutes: int


class ConfigResponse(BaseModel):
    train_id: str
    formation: str
    total_cars: int
    capacity_per_car: int
    cameras: List[dict] = []
