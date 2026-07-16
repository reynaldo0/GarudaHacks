"""
PROJECT THEMIS - Fusion Engine
Version: 5.0

Merges platform and cabin camera data for accurate occupancy.
"""

from typing import Dict, Optional
from loguru import logger


class FusionEngine:
    """Merges occupancy from multiple camera sources."""

    def __init__(self):
        pass

    def fuse(self, platform_occupancy: Dict = None, cabin_occupancy: Dict = None) -> Dict:
        """
        Fuse platform and cabin occupancy data.
        Cabin cameras are more accurate (inside the car).
        Platform cameras are secondary (boarding view).
        """
        if cabin_occupancy and platform_occupancy:
            # Cabin is primary, platform is secondary
            cabin_count = cabin_occupancy.get("person_count", 0)
            platform_count = platform_occupancy.get("person_count", 0)

            # Use max of both (more conservative)
            fused_count = max(cabin_count, platform_count)
            confidence = 0.9 if cabin_count > 0 else 0.7

            return {
                "person_count": fused_count,
                "capacity": cabin_occupancy.get("capacity", 200),
                "source": "fused",
                "confidence": confidence,
                "platform_count": platform_count,
                "cabin_count": cabin_count,
            }

        elif cabin_occupancy:
            cabin_occupancy["source"] = "cabin"
            cabin_occupancy["confidence"] = 0.9
            return cabin_occupancy

        elif platform_occupancy:
            platform_occupancy["source"] = "platform"
            platform_occupancy["confidence"] = 0.7
            return platform_occupancy

        return {
            "person_count": 0,
            "capacity": 200,
            "source": "none",
            "confidence": 0.0,
        }
