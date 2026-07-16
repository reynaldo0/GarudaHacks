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
                "total_cars": 10,
                "capacity_per_car": 200,
            },
            "occupancy": {
                "low_threshold": 0.4,
                "normal_threshold": 0.7,
                "high_threshold": 0.9,
                "full_threshold": 1.0,
            },
            "cameras": [
                {
                    "id": "platform_01",
                    "type": "platform",
                    "zone": "A",
                    "car_mapping": 1,
                    "status": "online",
                },
                {
                    "id": "cabin_04",
                    "type": "cabin",
                    "zone": "cabin_4",
                    "car_mapping": 4,
                    "status": "online",
                },
            ],
            "ai": {
                "model": "YOLO11s",
                "confidence": 0.5,
                "image_size": 640,
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
                {"camera_id": "platform_01", "zone": "A", "car_id": 1},
                {"camera_id": "platform_02", "zone": "B", "car_id": 2},
                {"camera_id": "platform_03", "zone": "C", "car_id": 3},
                {"camera_id": "cabin_04", "zone": "cabin_4", "car_id": 4},
                {"camera_id": "cabin_05", "zone": "cabin_5", "car_id": 5},
            ],
        },
    }
