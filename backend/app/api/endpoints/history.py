from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


@router.get("/history")
async def get_history(
    hours: int = Query(24, description="Number of hours to look back"),
    car_id: Optional[int] = Query(None, description="Filter by car ID"),
):
    """
    Get historical occupancy data.
    """
    # TODO: Query from SQLite database
    return {
        "success": True,
        "data": {
            "query": {
                "hours": hours,
                "car_id": car_id,
            },
            "records": [
                {
                    "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "car_id": 4,
                    "occupancy": 0.5 + (i * 0.02),
                    "status": "NORMAL",
                }
                for i in range(min(hours, 24))
            ],
            "summary": {
                "average_occupancy": 0.65,
                "peak_occupancy": 0.95,
                "peak_time": "08:30",
                "total_records": hours,
            },
        },
    }


@router.get("/history/warnings")
async def get_warning_history(
    hours: int = Query(24, description="Number of hours to look back"),
):
    """Get warning history."""
    return {
        "success": True,
        "data": {
            "warnings": [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "type": "HIGH_OCCUPANCY",
                    "severity": "WARNING",
                    "car_id": 4,
                    "message": "Car 4 occupancy reached 95%",
                }
            ],
        },
    }
