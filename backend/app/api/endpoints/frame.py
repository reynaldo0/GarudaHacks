"""
PROJECT THEMIS - Frame Endpoint
Version: 5.0

This endpoint handles frame upload from Unity Camera or other sources.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from app.core.state_manager import state_manager
from app.ai.yolo_engine import YOLOEngine
from app.ai.occupancy_engine import OccupancyEngine
from app.ai.lookup_table import LookupTable
from app.ai.fusion_engine import FusionEngine
from app.ai.cales_engine import CALESEngine
from app.ai.decision_engine import DecisionEngine

router = APIRouter()


@router.post("/frame")
async def receive_frame(
    file: UploadFile = File(...),
    camera_id: str = "default",
    station_id: str = "unknown",
    train_id: str = "SF10-001",
):
    """
    Receive frame from camera source.

    Flow:
    1. Receive JPEG frame
    2. Validate frame
    3. Decode with VideoAdapter
    4. Run YOLO detection
    5. Calculate occupancy
    6. Generate decision
    7. Update State Manager
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected image.")

    # Read frame data
    frame_data = await file.read()

    # Validate frame size
    if len(frame_data) == 0:
        raise HTTPException(status_code=400, detail="Empty frame.")

    # Get AI engines from main module
    import main
    yolo = main.yolo_engine
    occupancy = main.occupancy_engine
    lookup = main.lookup_table
    decision = main.decision_engine

    persons_detected = 0
    occupancy_data = None
    warning = None

    if yolo and yolo.is_loaded:
        # Decode frame
        import numpy as np
        import cv2
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            # YOLO detection
            detections = yolo.detect(frame)
            persons_detected = len(detections)

            # Get car ID from lookup table
            car_id = lookup.get_car_id(camera_id) or 1

            # Calculate occupancy
            occupancy_data = occupancy.calculate(persons_detected, capacity=200)
            occupancy_data["car_id"] = car_id

            # Update State Manager
            state_manager.update_car_occupancy(
                train_id=train_id,
                car_id=car_id,
                detected_persons=persons_detected,
                capacity=200,
                camera_id=camera_id,
            )

            # Generate warning
            if decision:
                warning = decision.evaluate(occupancy_data, train_id)

    return {
        "success": True,
        "data": {
            "frame_id": f"frame_{datetime.utcnow().timestamp()}",
            "camera_id": camera_id,
            "station_id": station_id,
            "train_id": train_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed",
            "persons_detected": persons_detected,
            "occupancy": occupancy_data,
            "warning": warning.model_dump() if warning else None,
        },
    }
