"""
PROJECT THEMIS - Video Adapter
Version: 6.0

Handles frame decoding, fisheye undistortion, and preprocessing.
"""

import cv2
import numpy as np
from typing import Optional, List
from loguru import logger

from app.config.settings import settings


class VideoAdapter:
    """Decodes and preprocesses video frames with fisheye support."""

    def __init__(self):
        self.calibration_dir = settings.FISHEYE_CALIBRATION_DIR
        self._load_calibration()

    def _load_calibration(self):
        """Load fisheye camera calibration data."""
        self.K = np.array(settings.fisheye_k) if settings.fisheye_k else None
        self.D = np.array(settings.fisheye_d) if settings.fisheye_d else None
        self.calibration_loaded = self.K is not None and self.D is not None

        if self.calibration_loaded:
            logger.info("Fisheye calibration loaded")
        else:
            logger.warning("No fisheye calibration data, undistortion disabled")

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

    def undistort_fisheye(self, frame: np.ndarray) -> np.ndarray:
        """
        Undistort fisheye image using calibration data.

        Args:
            frame: Input fisheye frame

        Returns:
            Undistorted frame
        """
        if frame is None:
            return frame

        if not self.calibration_loaded:
            return frame

        try:
            h, w = frame.shape[:2]
            new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
                self.K, self.D, (w, h), np.eye(3), balance=1.0
            )
            undistorted = cv2.fisheye.undistortImage(
                frame, self.K, self.D, np.eye(3), new_K
            )
            return undistorted
        except Exception as e:
            logger.error(f"Fisheye undistortion error: {e}")
            return frame

    def preprocess(self, frame: np.ndarray, target_size: tuple = (640, 640)) -> np.ndarray:
        """Resize and normalize frame for segmentation."""
        if frame is None:
            return frame
        resized = cv2.resize(frame, target_size)
        return resized

    def normalize(self, frame: np.ndarray) -> np.ndarray:
        """Normalize frame to 0-1 float range."""
        if frame is None:
            return frame
        return frame.astype(np.float32) / 255.0

    def to_rgb(self, frame: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB."""
        if frame is None:
            return frame
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert to grayscale."""
        if frame is None:
            return frame
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def extract_region(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Extract region of interest from frame."""
        if frame is None:
            return frame
        return frame[y1:y2, x1:x2]

    def process_frame(self, frame_data: bytes, target_size: tuple = (640, 640)) -> Optional[np.ndarray]:
        """
        Full preprocessing pipeline:
        1. Decode
        2. Undistort fisheye
        3. Resize
        4. Normalize
        """
        frame = self.decode_frame(frame_data)
        if frame is None:
            return None

        frame = self.undistort_fisheye(frame)
        frame = self.preprocess(frame, target_size)

        return frame

    def process_frames_batch(self, frames_data: List[bytes], target_size: tuple = (640, 640)) -> List[np.ndarray]:
        """Process multiple frames."""
        results = []
        for frame_data in frames_data:
            processed = self.process_frame(frame_data, target_size)
            if processed is not None:
                results.append(processed)
        return results
