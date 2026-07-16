"""
PROJECT THEMIS - Frame Receiver
Version: 5.0

Receives and validates frames from camera sources.
"""

import base64
import time
from typing import Optional
from loguru import logger

from app.ai.video_adapter import VideoAdapter


class FrameReceiver:
    """Receives, validates, and forwards frames."""

    def __init__(self):
        self.video_adapter = VideoAdapter()
        self._frame_count = 0

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

    def decode(self, frame_data: bytes):
        """Decode frame using VideoAdapter."""
        return self.video_adapter.decode_frame(frame_data)

    @property
    def frame_count(self) -> int:
        return self._frame_count
