from ._renderer_test import *


# Cached interface instance pointer
def get_renderer_test_interface() -> IRendererTest:
    if not hasattr(get_renderer_test_interface, "renderer_test"):
        get_renderer_test_interface.renderer_test = acquire_renderer_test_interface()
    return get_renderer_test_interface.renderer_test
