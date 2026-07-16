"""
PROJECT THEMIS - Frame Endpoint
Version: 6.0

This endpoint handles frame upload from Unity 4 ceiling fisheye cameras.
Full AI pipeline: Spatial Segmentation -> Occupancy Grid -> Fusion -> CALES -> Decision -> State
"""

import asyncio
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends, Form
from datetime import datetime
from typing import Optional, List
from app.core.state_manager import state_manager
from app.core.integration_hub import integration_hub
from app.core.security import verify_api_key

router = APIRouter()

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
    files: List[UploadFile] = File(...),
    camera_ids: Optional[str] = Form(default=None),
    station_id: str = Form(default="unknown"),
    train_id: str = Form(default="SF10-001"),
    _auth=Depends(verify_api_key_header),
):
    """
    Receive frames from 4 ceiling fisheye cameras per car.

    Pipeline:
    1. Receive 4 JPEG/PNG frames
    2. Fisheye undistortion
    3. Spatial Occupancy Segmentation
    4. Occupancy Grid Generation
    5. Fusion (4 grids -> 1 car map)
    6. Density Classification
    7. CALES (Bogie Health)
    8. Redistribution Analysis
    9. Door Logic
    10. Announcement Generation
    11. PipelineState Construction
    12. WebSocket Broadcast
    """
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    frames_data = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")
        data = await file.read()
        if len(data) == 0:
            raise HTTPException(status_code=400, detail="Empty frame.")
        frames_data.append(data)

    # Parse camera IDs
    cam_ids = []
    if camera_ids:
        cam_ids = [c.strip() for c in camera_ids.split(",")]
    while len(cam_ids) < len(files):
        cam_ids.append(f"cam{len(cam_ids)+1:02d}")

    async with _frame_semaphore:
        result = await asyncio.to_thread(
            _process_frames, frames_data, cam_ids, train_id, station_id
        )

    await _broadcast_pipeline_state(result, train_id)

    return result


def _process_frames(
    frames_data: List[bytes],
    camera_ids: List[str],
    train_id: str,
    station_id: str,
) -> dict:
    """
    Synchronous frame processing (runs in thread pool).
    Pipeline: Spatial Segmentation -> Occupancy Grid -> Fusion -> CALES -> Decision -> State
    """
    import main
    spatial = main.spatial_engine
    occupancy = main.occupancy_engine
    lookup = main.lookup_table
    fusion = main.fusion_engine
    cales = main.cales_engine
    decision = main.decision_engine
    redistribution = main.redistribution_engine
    door = main.door_engine
    announcement = main.announcement_engine

    # Get car ID from first camera
    car_id = lookup.get_car_id(camera_ids[0]) or 1

    # 1. Preprocess all frames (fisheye undistortion + resize)
    from app.ai.video_adapter import VideoAdapter
    adapter = VideoAdapter()

    camera_results = []
    for frame_data, cam_id in zip(frames_data, camera_ids):
        frame = adapter.decode_frame(frame_data)
        if frame is None:
            continue

        # Fisheye undistortion
        frame = adapter.undistort_fisheye(frame)

        # Resize
        frame = adapter.preprocess(frame, (640, 640))

        # 2. Spatial Occupancy Segmentation
        result = spatial.predict(frame)
        camera_results.append(result)

    # 3. Fusion - merge 4 occupancy grids
    fused = fusion.fuse(camera_results)

    # 4. Calculate occupancy metrics
    occ_metrics = occupancy.calculate(
        spatial_occupancy_score=fused.get("spatial_occupancy_score", 0),
        free_space_ratio=fused.get("free_space_ratio", 1.0),
    )

    # 5. Density classification
    from app.ai.density_classifier import DensityClassifier
    classifier = DensityClassifier()
    density_result = classifier.classify(fused)

    # 6. CALES - Bogie Health
    cales.add_snapshot(
        car_id,
        fused.get("spatial_occupancy_score", 0),
        occ_metrics.get("occupancy_ratio", 0),
    )

    # Get all car data for CALES calculation
    all_car_data = _get_all_car_data(train_id)
    cales_result = cales.calculate_cales_score(car_id, all_car_data)

    # 7. Redistribution Analysis
    redistribution_result = redistribution.analyze(
        all_car_data + [{"car_id": car_id, **occ_metrics}],
        current_car_id=car_id,
    )

    # 8. Door Logic
    door_result = door.evaluate(
        car_id,
        density_result.get("density_indicator", "GREEN"),
        redistribution_result,
    )

    # 9. Announcement
    announcement_result = announcement.generate(redistribution_result, car_id)

    # 10. Warning
    warning = decision.evaluate(
        {"car_id": car_id, **occ_metrics, "density_indicator": density_result.get("density_indicator")},
        train_id,
    )

    # 11. Update State Manager
    state_manager.update_car_spatial_occupancy(
        train_id=train_id,
        car_id=car_id,
        occupancy_ratio=occ_metrics.get("occupancy_ratio", 0),
        free_space_ratio=occ_metrics.get("free_space_ratio", 1),
        spatial_occupancy_score=fused.get("spatial_occupancy_score", 0),
        density_indicator=density_result.get("density_indicator", "GREEN"),
        camera_id=camera_ids[0] if camera_ids else None,
    )

    # 12. Build PipelineState
    pipeline_state = {
        "car_id": f"car_{car_id:02d}",
        "occupancy_ratio": occ_metrics.get("occupancy_ratio", 0),
        "free_space_ratio": occ_metrics.get("free_space_ratio", 1),
        "density_indicator": density_result.get("density_indicator", "GREEN"),
        "spatial_occupancy_score": fused.get("spatial_occupancy_score", 0),
        "recommended_target": redistribution_result.get("to_car_id") if redistribution_result else None,
        "door_action": door_result.get("door_action", "CLOSE"),
        "announcement": announcement_result.get("text") if announcement_result else None,
        "cales_score": cales_result.get("cales_score", 0),
        "health_index": cales_result.get("health_index", 100),
        "damage_multiplier": cales_result.get("damage_multiplier", 1.0),
        "inspection_priority": 0,
        "recommended_action": "CONTINUE_MONITORING",
        "timestamp": datetime.utcnow().isoformat(),
    }

    return {
        "success": True,
        "data": pipeline_state,
    }


def _get_all_car_data(train_id: str) -> list:
    """Get all car data from state manager."""
    train_state = state_manager.get_train_state(train_id)
    if not train_state:
        return []

    return [
        {
            "car_id": c.car_id,
            "occupancy_ratio": getattr(c, 'occupancy_ratio', 0),
            "spatial_occupancy_score": getattr(c, 'spatial_occupancy_score', 0),
            "density_indicator": getattr(c, 'density_indicator', 'GREEN'),
        }
        for c in train_state.cars
    ]


async def _broadcast_pipeline_state(result: dict, train_id: str):
    """Broadcast pipeline state via WebSocket."""
    try:
        data = result.get("data", {})
        await integration_hub.broadcast_pipeline_state_updated(
            pipeline_state=data,
            train_id=train_id,
        )
    except Exception as e:
        print(f"[Frame] Broadcast error: {e}")
