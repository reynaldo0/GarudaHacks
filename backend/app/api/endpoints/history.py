"""
PROJECT THEMIS - History Endpoint
Version: 5.0

Provides historical occupancy & warning data.
Occupancy trend is derived from current live state (sandbox demo),
warnings come from the State Manager log.
"""

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional
import random

from app.core.state_manager import state_manager

router = APIRouter()


@router.get("/history")
async def get_history(
    hours: int = Query(24, description="Number of hours to look back"),
    car_id: Optional[int] = Query(None, description="Filter by car ID"),
):
    """Get historical occupancy data (synthesized from current live state)."""
    trains = state_manager.get_all_trains()
    base_occ = 0.5
    if trains and trains[0].cars:
        cars = trains[0].cars
        if car_id:
            match = next((c for c in cars if c.car_id == car_id), None)
            if match:
                base_occ = getattr(match, 'occupancy_ratio', 0.5)
        else:
            base_occ = sum(getattr(c, 'occupancy_ratio', 0) for c in cars) / (len(cars) * 1.0) if cars else 0.5

    points = min(max(hours, 1), 24)
    rng = random.Random(42 + (car_id or 0))
    records = []
    for i in range(points):
        variation = rng.uniform(-0.12, 0.12)
        occ = max(0.0, min(1.0, base_occ + variation - (i * 0.005)))
        if occ < 0.4:
            density = "GREEN"
        elif occ < 0.7:
            density = "YELLOW"
        else:
            density = "RED"
        records.append(
            {
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "car_id": car_id or 4,
                "occupancy_ratio": round(occ, 4),
                "density_indicator": density,
            }
        )

    avg = sum(r["occupancy_ratio"] for r in records) / len(records) if records else 0
    peak = max((r["occupancy_ratio"] for r in records), default=0)

    return {
        "success": True,
        "data": {
            "query": {"hours": hours, "car_id": car_id},
            "records": records,
            "summary": {
                "average_occupancy": round(avg, 3),
                "peak_occupancy": round(peak, 3),
                "peak_time": "08:30",
                "total_records": len(records),
            },
        },
    }


@router.get("/history/warnings")
async def get_warning_history(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get warning history from the State Manager."""
    warnings = state_manager.get_active_warnings()
    data = []
    for w in warnings:
        data.append(
            {
                "id": f"{w.train_id}-{w.car_id}-{w.warning_type}",
                "timestamp": w.timestamp.isoformat() if w.timestamp else datetime.utcnow().isoformat(),
                "warningType": w.warning_type,
                "severity": w.severity,
                "carId": w.car_id,
                "message": w.message,
                "trainId": w.train_id,
                "isActive": w.is_active,
            }
        )

    return {
        "success": True,
        "data": {
            "warnings": data,
            "total": len(data),
            "hours": hours,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }