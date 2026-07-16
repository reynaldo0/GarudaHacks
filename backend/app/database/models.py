"""
PROJECT THEMIS - Database Models
Version: 6.0

SQLAlchemy models for PostgreSQL database.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class OccupancyHistory(Base):
    """Store spatial occupancy history for each car."""

    __tablename__ = "occupancy_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    station_id = Column(String(50), nullable=False)
    occupancy_ratio = Column(Float, default=0.0)        # 0.0 - 1.0
    free_space_ratio = Column(Float, default=1.0)        # 0.0 - 1.0
    spatial_occupancy_score = Column(Float, default=0.0)  # 0.0 - 1.0
    density_indicator = Column(String(20), default="GREEN")  # GREEN, YELLOW, RED
    floor_area_m2 = Column(Float, default=42.0)
    camera_id = Column(String(100), nullable=True)


class PredictionHistory(Base):
    """Store prediction history based on spatial occupancy."""

    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    predicted_occupancy_ratio = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    prediction_horizon_minutes = Column(Integer, default=15)


class WarningHistory(Base):
    """Store warning history."""

    __tablename__ = "warning_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    warning_type = Column(String(50), nullable=False)  # HIGH_DENSITY, RED_DENSITY
    severity = Column(String(20), nullable=False)  # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class DecisionHistory(Base):
    """Store decision/recommendation history."""

    __tablename__ = "decision_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    from_car_id = Column(Integer, nullable=False)
    to_car_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=False)  # REDISTRIBUTION, DOOR_OPEN, DOOR_CLOSE
    door_action = Column(String(50), nullable=True)  # OPEN_MIDDLE, CLOSE
    announcement = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)


class CameraConfiguration(Base):
    """Store camera configuration - 4 ceiling fisheye cameras per car."""

    __tablename__ = "camera_configuration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(100), unique=True, nullable=False)
    camera_type = Column(String(50), nullable=False)  # ceiling_fisheye
    zone = Column(String(50), nullable=False)
    car_mapping = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    url = Column(String(500), nullable=True)
    fps = Column(Integer, default=1)


class TrainConfiguration(Base):
    """Store train configuration."""

    __tablename__ = "train_configuration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    train_id = Column(String(50), unique=True, nullable=False)
    formation = Column(String(20), nullable=False)  # SF10
    total_cars = Column(Integer, nullable=False)
    capacity_per_car = Column(Integer, default=200)
    floor_area_m2 = Column(Float, default=42.0)
    is_active = Column(Boolean, default=True)


class BogieHistory(Base):
    """Store bogie maintenance history (CALES)."""

    __tablename__ = "bogie_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    cales_score = Column(Float, default=0.0)
    health_index = Column(Float, default=100.0)
    damage_multiplier = Column(Float, default=1.0)
    inspection_priority = Column(Integer, default=0)
    recommended_action = Column(String(100), default="CONTINUE_MONITORING")


class SystemLog(Base):
    """Store system logs."""

    __tablename__ = "system_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(50), nullable=False)  # Spatial, Occupancy, Decision, etc.
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
