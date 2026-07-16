"""
PROJECT THEMIS - YOLO Engine
Version: 5.0

Person detection engine using YOLO11s.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional
from loguru import logger

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
    logger.warning("ultralytics not installed")


class YOLOEngine:
    """YOLO-based person detection engine."""

    def __init__(self, model_path: str = "weights/yolo11s.pt", confidence: float = 0.5):
        self.model_path = model_path
        self.confidence = confidence
        self.model = None
        self._loaded = False

    def load(self) -> bool:
        """Load YOLO model."""
        if YOLO is None:
            logger.error("ultralytics not available")
            return False
        try:
            self.model = YOLO(self.model_path)
            self._loaded = True
            logger.info(f"YOLO model loaded: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return False

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect persons in frame.
        Returns list of detections with bbox, confidence.
        """
        if not self._loaded or self.model is None:
            return []

        results = self.model(frame, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    # Class 0 = person
                    if cls == 0 and conf >= self.confidence:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        detections.append({
                            "class_id": cls,
                            "class_name": "person",
                            "confidence": round(conf, 4),
                            "bbox": {
                                "x1": round(x1, 2),
                                "y1": round(y1, 2),
                                "x2": round(x2, 2),
                                "y2": round(y2, 2),
                            },
                            "area": round((x2 - x1) * (y2 - y1), 2),
                        })

        return detections

    def get_person_count(self, frame: np.ndarray) -> int:
        """Get count of persons detected in frame."""
        return len(self.detect(frame))

    @property
    def is_loaded(self) -> bool:
        return self._loaded
