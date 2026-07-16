from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime

router = APIRouter()


@router.post("/frame")
async def receive_frame(
    file: UploadFile = File(...),
    camera_id: str = "default",
    station_id: str = "unknown",
    train_id: str = "unknown",
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected image.")

    frame_data = await file.read()

    if len(frame_data) == 0:
        raise HTTPException(status_code=400, detail="Empty frame.")

    return {
        "success": True,
        "data": {
            "frame_id": f"frame_{datetime.now().timestamp()}",
            "camera_id": camera_id,
            "station_id": station_id,
            "train_id": train_id,
            "timestamp": datetime.now().isoformat(),
            "status": "received",
        },
    }
