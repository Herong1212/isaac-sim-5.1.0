"This is an extension to capture different graphics resources to a file."

from .scripts.extension import *
from omni.kit.renderer_capture import acquire_renderer_capture_interface, IRendererCapture

__all__ = [
    "acquire_renderer_capture_interface",
    "IRendererCapture",
]
