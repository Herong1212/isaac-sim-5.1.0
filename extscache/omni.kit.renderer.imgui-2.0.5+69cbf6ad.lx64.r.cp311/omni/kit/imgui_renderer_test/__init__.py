from ._imgui_renderer_test import *


# Cached interface instance pointer
def get_imgui_renderer_test_interface() -> IImGuiRendererTest:
    if not hasattr(get_imgui_renderer_test_interface, "imgui_renderer_test"):
        get_imgui_renderer_test_interface.imgui_renderer_test = acquire_imgui_renderer_test_interface()
    return get_imgui_renderer_test_interface.imgui_renderer_test
