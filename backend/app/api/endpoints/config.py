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
            "cameras": [
                {
                    "id": "platform_01",
                    "type": "platform",
                    "zone": "A",
                    "carMapping": 1,
                    "status": "online",
                },
                {
                    "id": "cabin_04",
                    "type": "cabin",
                    "zone": "cabin_4",
                    "carMapping": 4,
                    "status": "online",
                },
            ],
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
    return {
        "success": True,
        "data": {
            "mappings": [
                {"cameraId": "platform_01", "zone": "A", "carId": 1},
                {"cameraId": "platform_02", "zone": "B", "carId": 2},
                {"cameraId": "platform_03", "zone": "C", "carId": 3},
                {"cameraId": "cabin_04", "zone": "cabin_4", "carId": 4},
                {"cameraId": "cabin_05", "zone": "cabin_5", "carId": 5},
            ],
        },
    }
