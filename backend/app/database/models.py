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
    """Store occupancy history for each car."""

    __tablename__ = "occupancy_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    station_id = Column(String(50), nullable=False)
    detected_persons = Column(Integer, default=0)
    capacity = Column(Integer, default=200)
    occupancy_percentage = Column(Float, default=0.0)
    status = Column(String(20), default="LOW")
    camera_id = Column(String(100), nullable=True)


class PredictionHistory(Base):
    """Store prediction history."""

    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    car_id = Column(Integer, nullable=False)
    predicted_occupancy = Column(Float, default=0.0)
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
    warning_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class DecisionHistory(Base):
    """Store decision/recommendation history."""

    __tablename__ = "decision_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    train_id = Column(String(50), nullable=False)
    from_car_id = Column(Integer, nullable=False)
    to_car_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # MOVE_PASSENGER
    confidence = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)


class CameraConfiguration(Base):
    """Store camera configuration."""

    __tablename__ = "camera_configuration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(100), unique=True, nullable=False)
    camera_type = Column(String(50), nullable=False)  # platform, cabin
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
    formation = Column(String(20), nullable=False)  # SF8, SF10, SF12
    total_cars = Column(Integer, nullable=False)
    capacity_per_car = Column(Integer, default=200)
    is_active = Column(Boolean, default=True)


class SystemLog(Base):
    """Store system logs."""

    __tablename__ = "system_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(50), nullable=False)  # YOLO, Occupancy, Decision, etc.
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
