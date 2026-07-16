"""
PROJECT THEMIS - Configuration Endpoint
Version: 5.0

This endpoint provides system configuration.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/config")
async def get_config():
    """
    Get current system configuration.
    """
    cameras = []
    for i in range(1, 11):
        for j in range(1, 3):
            cam_id = f"car{str(i).zfill(2)}_cam{str(j).zfill(2)}"
            cameras.append({
                "id": cam_id,
                "type": "cabin",
                "zone": f"car_{i}",
                "carMapping": i,
                "status": "online",
            })

    return {
        "success": True,
        "data": {
            "train": {
                "formation": "SF10",
                "totalCars": 10,
                "capacityPerCar": 200,
            },
            "occupancy": {
                "lowThreshold": 0.4,
                "normalThreshold": 0.7,
                "highThreshold": 0.9,
                "fullThreshold": 1.0,
            },
            "cameras": cameras,
            "ai": {
                "model": "YOLO11s",
                "confidence": 0.5,
                "imageSize": 640,
            },
        },
    }


@router.get("/config/lookup-table")
async def get_lookup_table():
    """Get camera to car mapping lookup table."""
    mappings = []
    for i in range(1, 11):
        for j in range(1, 3):
            cam_id = f"car{str(i).zfill(2)}_cam{str(j).zfill(2)}"
            mappings.append({
                "cameraId": cam_id,
                "zone": f"car_{i}",
                "carId": i,
            })

    return {
        "success": True,
        "data": {
            "mappings": mappings,
        },
    }
