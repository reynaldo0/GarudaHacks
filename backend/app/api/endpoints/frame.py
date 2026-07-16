"""
PROJECT THEMIS - Frame Endpoint
Version: 7.0

This endpoint handles frame upload from Unity Camera or other sources.
Full AI pipeline: YOLO -> Occupancy -> Fusion -> CALES -> Decision -> State
Async-safe: YOLO runs in thread pool via asyncio.to_thread.

YOLO IS THE ONLY DETECTION SOURCE. No Unity fallback.
"""

import asyncio
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from datetime import datetime
from typing import Optional
from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub
from app.core.security import verify_api_key

router = APIRouter()

# Semaphore to limit concurrent frame processing (prevents YOLO overload)
_frame_semaphore = asyncio.Semaphore(5)


async def verify_api_key_header(
    x_api_key: Optional[str] = Header(default=None),
):
    """Verify Unity API key for frame uploads."""
    if x_api_key and verify_api_key(x_api_key):
        return {"source": "api_key"}
    raise HTTPException(
        status_code=401,
        detail="Valid X-API-Key header required for frame uploads.",
    )


@router.post("/frame")
async def receive_frame(
    file: UploadFile = File(...),
    camera_id: str = "default",
    station_id: str = "unknown",
    train_id: str = "SF10-001",
    _auth=Depends(verify_api_key_header),
):
    """
    Receive frame from camera source.

    YOLO is the SOLE detection source. Pipeline:
    1. Receive JPEG frame
    2. Run YOLO detection in thread pool (non-blocking)
    3. Calculate occupancy from YOLO results
    4. Fuse with existing data (FusionEngine)
    5. Predict trend (CALESEngine)
    6. Generate warning (DecisionEngine)
    7. Update State Manager
    8. Broadcast via WebSocket
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected image.")

    frame_data = await file.read()

    if len(frame_data) == 0:
        raise HTTPException(status_code=400, detail="Empty frame.")

    # Run YOLO + AI pipeline in thread pool (does not block event loop)
    async with _frame_semaphore:
        result = await asyncio.to_thread(
            _process_frame, frame_data, camera_id, train_id
        )

    # Broadcast results via WebSocket (async, fast)
    await _broadcast_results(result, camera_id, train_id)

    return result


def _process_frame(
    frame_data: bytes,
    camera_id: str,
    train_id: str,
) -> dict:
    """
    Synchronous frame processing (runs in thread pool).
    YOLO IS THE ONLY DETECTION SOURCE. No fallback to Unity.
    Pipeline: YOLO -> Occupancy -> Fusion -> CALES -> Decision -> State
    """
    import main
    yolo = main.yolo_engine
    occupancy = main.occupancy_engine
    lookup = main.lookup_table
    fusion = main.fusion_engine
    cales = main.cales_engine
    decision = main.decision_engine

    persons_detected = 0
    occupancy_data = None
    warning = None
    prediction = None
    recommendation = None

    if yolo and yolo.is_loaded:
        import numpy as np
        import cv2
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            # 1. YOLO detection - THE ONLY SOURCE
            detections = yolo.detect(frame)
            persons_detected = len(detections)

            # 2. Get car ID from lookup table
            car_id = lookup.get_car_id(camera_id) or 1
            camera_type = lookup.get_camera_type(camera_id) or "cabin"

            # 3. Calculate occupancy from YOLO result
            raw_occupancy = occupancy.calculate(persons_detected, capacity=200)
            raw_occupancy["car_id"] = car_id

            # 4. Fusion - merge with existing state
            existing_car = None
            train_state = state_manager.get_train_state(train_id)
            if train_state:
                for c in train_state.cars:
                    if c.car_id == car_id:
                        existing_car = {
                            "person_count": c.detected_persons,
                            "capacity": c.capacity,
                            "occupancy_percentage": c.occupancy_percentage,
                        }
                        break

            fused = fusion.fuse(
                platform_occupancy=raw_occupancy if camera_type == "platform" else existing_car,
                cabin_occupancy=raw_occupancy if camera_type == "cabin" else existing_car,
            )
            fused["car_id"] = car_id

            # 5. CALES - predict and add snapshot
            cales.add_snapshot(car_id, fused.get("occupancy_percentage", 0), persons_detected)
            prediction = cales.predict(car_id)

            # 6. Decision - generate warning
            occupancy_data = occupancy.calculate(fused.get("person_count", persons_detected), capacity=200)
            occupancy_data["car_id"] = car_id
            if decision:
                warning = decision.evaluate(occupancy_data, train_id)

            # 7. Update State Manager
            state_manager.update_car_occupancy(
                train_id=train_id,
                car_id=car_id,
                detected_persons=fused.get("person_count", persons_detected),
                capacity=200,
                camera_id=camera_id,
            )

            # 8. Generate recommendation from CALES
            train_state = state_manager.get_train_state(train_id)
            if train_state and cales:
                recommendation = cales.generate_recommendation(
                    [{"car_id": c.car_id, "occupancy_percentage": c.occupancy_percentage} for c in train_state.cars]
                )
    else:
        # YOLO not loaded - cannot detect. Return 0.
        print(f"[Frame] WARNING: YOLO not loaded, cannot detect persons for {camera_id}")

    return {
        "success": True,
        "data": {
            "frame_id": f"frame_{time.time()}",
            "camera_id": camera_id,
            "station_id": station_id,
            "train_id": train_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed",
            "persons_detected": persons_detected,
            "detection_source": "yolo",
            "occupancy": occupancy_data,
            "prediction": prediction,
            "recommendation": recommendation,
            "warning": warning.model_dump() if warning else None,
        },
    }


async def _broadcast_results(result: dict, camera_id: str, train_id: str):
    """Broadcast frame processing results via WebSocket."""
    try:
        data = result.get("data", {})

        if data.get("occupancy"):
            await integration_hub.broadcast_occupancy_updated(
                car_id=data["occupancy"].get("car_id", 1),
                occupancy_data=data["occupancy"],
                train_id=train_id,
            )

        if data.get("prediction"):
            await integration_hub.broadcast_prediction_updated(
                car_id=data["occupancy"].get("car_id", 1) if data.get("occupancy") else 1,
                prediction=data["prediction"],
                train_id=train_id,
            )

        if data.get("recommendation"):
            await integration_hub.broadcast_recommendation_changed(
                recommendation=data["recommendation"],
                train_id=train_id,
            )

        if data.get("warning"):
            await integration_hub.broadcast_warning_updated(
                warning=data["warning"],
                train_id=train_id,
            )

        await integration_hub.broadcast_camera_status_updated(
            camera_id=camera_id,
            status="active",
            train_id=train_id,
        )
    except Exception as e:
        print(f"[Frame] Broadcast error: {e}")
