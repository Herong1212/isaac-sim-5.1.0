import functools
from ._renderer_capture_test import *


# Cached interface instance pointer
@functools.lru_cache()
def get_renderer_capture_test_interface() -> IRendererCaptureTest:
    if not hasattr(get_renderer_capture_test_interface, "renderer_capture_test"):
        get_renderer_capture_test_interface.renderer_capture_test = acquire_renderer_capture_test_interface()
    return get_renderer_capture_test_interface.renderer_capture_test
