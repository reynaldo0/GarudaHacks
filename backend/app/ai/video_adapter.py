"""
PROJECT THEMIS - Video Adapter
Version: 5.0

Handles frame decoding and preprocessing.
"""

import cv2
import numpy as np
from typing import Optional
from loguru import logger


class VideoAdapter:
    """Decodes and preprocesses video frames."""

    def __init__(self):
        pass

    def decode_frame(self, frame_data: bytes) -> Optional[np.ndarray]:
        """Decode JPEG/PNG bytes to numpy array."""
        try:
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                logger.warning("Failed to decode frame")
                return None
            return frame
        except Exception as e:
            logger.error(f"Frame decode error: {e}")
            return None

    def preprocess(self, frame: np.ndarray, target_size: tuple = (640, 640)) -> np.ndarray:
        """Resize and normalize frame for YOLO."""
        if frame is None:
            return frame
        resized = cv2.resize(frame, target_size)
        return resized

    def to_rgb(self, frame: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB."""
        if frame is None:
            return frame
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def extract_region(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Extract region of interest from frame."""
        if frame is None:
            return frame
        return frame[y1:y2, x1:x2]
