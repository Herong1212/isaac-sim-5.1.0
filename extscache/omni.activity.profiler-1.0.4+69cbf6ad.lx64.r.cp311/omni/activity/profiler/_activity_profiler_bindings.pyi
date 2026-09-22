"""pybind11 omni.activity.profiler bindings"""
from __future__ import annotations
import omni.activity.profiler._activity_profiler_bindings
import typing

__all__ = [
    "CAPTURE_MASK_LATENCY",
    "CAPTURE_MASK_SCENE_LOADING",
    "CAPTURE_MASK_STARTUP",
    "IActivityProfiler",
    "acquire_activity_profiler",
    "release_activity_profiler"
]


class IActivityProfiler():
    """
    Interface to the activity carb profiler implementation.
    """
    def disable_capture_mask(self, unique_identifier: int) -> None: 
        """
        Disable a capture mask that was previously set, and disable the activity core if needed.

        Args:
            unique_identifier: The unique identifier returned from a call to enableCaptureMask.
        """
    def enable_capture_mask(self, capture_mask: int) -> int: 
        """
        Enable a capture mask for the activity profiler, and enable the activity core if needed.

        Args:
            capture_mask: Profiler capture mask to enable for the activity profiler.

        Return:
            A unique identifier that must be passed to disable_capture_mask.
        """
    pass
def acquire_activity_profiler(plugin_name: str = None, library_path: str = None) -> IActivityProfiler:
    pass
def release_activity_profiler(arg0: IActivityProfiler) -> None:
    pass
CAPTURE_MASK_LATENCY = 8589934592
CAPTURE_MASK_SCENE_LOADING = 4294967296
CAPTURE_MASK_STARTUP = 17179869184
