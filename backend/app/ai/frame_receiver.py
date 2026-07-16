"""
PROJECT THEMIS - Frame Receiver
Version: 6.0

Receives and validates frames from 4 ceiling fisheye cameras per car.
"""

import base64
import time
from typing import Optional, List, Dict
from loguru import logger

from app.ai.video_adapter import VideoAdapter


class FrameReceiver:
    """Receives, validates, and forwards frames from multiple cameras."""

    def __init__(self):
        self.video_adapter = VideoAdapter()
        self._frame_count = 0
        self._batch_count = 0

    def receive_base64(self, frame_base64: str) -> Optional[bytes]:
        """Decode base64 frame to bytes."""
        try:
            frame_bytes = base64.b64decode(frame_base64)
            if len(frame_bytes) == 0:
                logger.warning("Empty frame data")
                return None
            return frame_bytes
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return None

    def receive_bytes(self, frame_data: bytes) -> bool:
        """Validate frame bytes."""
        if not frame_data or len(frame_data) == 0:
            return False
        self._frame_count += 1
        return True

    def receive_batch(self, frames_data: List[bytes]) -> Dict:
        """
        Receive batch of frames from 4 cameras.

        Args:
            frames_data: List of 4 frame bytes (cam01, cam02, cam03, cam04)

        Returns:
            Dict with valid_frames list and metadata
        """
        valid_frames = []
        for i, frame_data in enumerate(frames_data):
            if self.receive_bytes(frame_data):
                valid_frames.append({
                    "camera_index": i,
                    "data": frame_data,
                })

        self._batch_count += 1

        return {
            "total_received": len(frames_data),
            "valid_count": len(valid_frames),
            "frames": valid_frames,
            "batch_id": self._batch_count,
            "timestamp": time.time(),
        }

    def decode(self, frame_data: bytes):
        """Decode frame using VideoAdapter."""
        return self.video_adapter.decode_frame(frame_data)

    def decode_batch(self, frames_data: List[bytes]) -> List:
        """Decode multiple frames."""
        return [self.video_adapter.decode_frame(fd) for fd in frames_data]

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def batch_count(self) -> int:
        return self._batch_count
