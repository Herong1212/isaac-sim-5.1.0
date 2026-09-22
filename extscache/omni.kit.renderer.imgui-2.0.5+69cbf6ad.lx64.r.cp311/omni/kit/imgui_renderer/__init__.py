from ._imgui_renderer import *


# Cached interface instance pointer
def get_imgui_renderer_interface() -> IImGuiRenderer:
    """Returns cached :class:`omni.kit.renderer.IImGuiRenderer` interface"""

    if not hasattr(get_imgui_renderer_interface, "imgui_renderer"):
        get_imgui_renderer_interface.imgui_renderer = acquire_imgui_renderer_interface()
    return get_imgui_renderer_interface.imgui_renderer
