from ._renderer import *

import carb

# Cached interface instance pointer
def get_renderer_interface() -> IRenderer:
    """Returns cached :class:`omni.kit.renderer.IRenderer` interface"""

    if not hasattr(get_renderer_interface, "renderer"):
        get_renderer_interface.renderer = acquire_renderer_interface()
    return get_renderer_interface.renderer

IRenderer.get_pre_begin_frame_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_pre_begin_frame_event_stream)
IRenderer.get_pre_begin_render_pass_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_pre_begin_render_pass_event_stream)
IRenderer.get_render_frame_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_render_frame_event_stream)
IRenderer.get_post_end_render_pass_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_post_end_render_pass_event_stream)
IRenderer.get_post_end_render_frame_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_post_end_render_frame_event_stream)
IRenderer.get_present_render_frame_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_present_render_frame_event_stream)
IRenderer.get_post_present_frame_buffer_event_stream = carb.deprecated("Use Events 2.0")(IRenderer.get_post_present_frame_buffer_event_stream)
