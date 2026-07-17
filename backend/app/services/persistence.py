"""
PROJECT THEMIS - Persistence Service
Version: 6.0

Persists AI pipeline results to the database after each frame upload.
Each Unity upload creates exactly ONE history record per applicable table.
"""

from datetime import datetime
from typing import Optional, List, Dict
from loguru import logger
from app.database.connection import SessionLocal
from app.database.models import (
    OccupancyHistory,
    PredictionHistory,
    WarningHistory,
    DecisionHistory,
    BogieHistory,
)


def persist_pipeline_result(
    train_id: str,
    car_id: int,
    station_id: str,
    camera_ids: List[str],
    occupancy_ratio: float,
    free_space_ratio: float,
    spatial_occupancy_score: float,
    density_indicator: str,
    cales_score: float,
    health_index: float,
    damage_multiplier: float,
    redistribution_result: Optional[Dict],
    door_action: str,
    announcement_text: Optional[str],
    warning=None,
    prediction_confidence: float = 0.8,
):
    """
    Persist all pipeline results to the database.
    Called synchronously at the end of _process_frames().
    Rollback on exception. Never leak sessions.
    """
    db = SessionLocal()
    try:
        # 1. OccupancyHistory — always saved
        db.add(OccupancyHistory(
            timestamp=datetime.utcnow(),
            train_id=train_id,
            car_id=car_id,
            station_id=station_id,
            occupancy_ratio=occupancy_ratio,
            free_space_ratio=free_space_ratio,
            spatial_occupancy_score=spatial_occupancy_score,
            density_indicator=density_indicator,
            floor_area_m2=42.0,
            camera_id=camera_ids[0] if camera_ids else None,
        ))

        # 2. PredictionHistory — always saved
        db.add(PredictionHistory(
            timestamp=datetime.utcnow(),
            train_id=train_id,
            car_id=car_id,
            predicted_occupancy_ratio=occupancy_ratio,
            risk_score=_calculate_risk(occupancy_ratio),
            confidence=prediction_confidence,
            prediction_horizon_minutes=15,
        ))

        # 3. WarningHistory — only when warning exists (RED/YELLOW)
        if warning is not None:
            db.add(WarningHistory(
                timestamp=getattr(warning, 'timestamp', None) or datetime.utcnow(),
                train_id=train_id,
                car_id=car_id,
                warning_type=getattr(warning, 'warning_type', 'UNKNOWN'),
                severity=getattr(warning, 'severity', 'INFO'),
                message=getattr(warning, 'message', ''),
                is_active=getattr(warning, 'is_active', True),
            ))

        # 4. DecisionHistory — only when redistribution is recommended
        if redistribution_result is not None:
            db.add(DecisionHistory(
                timestamp=datetime.utcnow(),
                train_id=train_id,
                from_car_id=redistribution_result.get("from_car_id", car_id),
                to_car_id=redistribution_result.get("to_car_id"),
                action=redistribution_result.get("action", "REDISTRIBUTION"),
                door_action=door_action,
                announcement=announcement_text,
                confidence=redistribution_result.get("confidence", 0.0),
                reason=redistribution_result.get("reason", ""),
            ))

        # 5. BogieHistory — always saved
        recommended_action = _get_cales_action(cales_score, health_index)
        inspection_priority = _get_inspection_priority(cales_score)

        db.add(BogieHistory(
            timestamp=datetime.utcnow(),
            train_id=train_id,
            car_id=car_id,
            cales_score=cales_score,
            health_index=health_index,
            damage_multiplier=damage_multiplier,
            inspection_priority=inspection_priority,
            recommended_action=recommended_action,
        ))

        db.commit()
        logger.debug(
            f"[Persistence] Saved train={train_id} car={car_id} "
            f"occ={occupancy_ratio:.2f} density={density_indicator}"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"[Persistence] Failed to persist pipeline result: {e}")
    finally:
        db.close()


def _calculate_risk(occupancy_ratio: float) -> float:
    if occupancy_ratio < 0.4:
        return 0.1
    elif occupancy_ratio < 0.7:
        return 0.4
    elif occupancy_ratio < 0.9:
        return 0.7
    else:
        return 1.0


def _get_cales_action(cales_score: float, health_index: float) -> str:
    if health_index < 30 or cales_score > 0.7:
        return "IMMEDIATE_DEPOT_INSPECTION"
    elif health_index < 60 or cales_score > 0.5:
        return "PRIORITY_INSPECTION"
    elif health_index < 80 or cales_score > 0.3:
        return "SCHEDULE_INSPECTION"
    return "CONTINUE_MONITORING"


def _get_inspection_priority(cales_score: float) -> int:
    if cales_score > 0.7:
        return 1
    elif cales_score > 0.5:
        return 2
    elif cales_score > 0.3:
        return 3
    return 0
