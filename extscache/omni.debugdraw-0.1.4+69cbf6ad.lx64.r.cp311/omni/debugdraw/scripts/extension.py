import omni.ext
from .._debugDraw import *

_debug_draw_api = None


def get_debug_draw_interface() -> IDebugDraw:
    return _debug_draw_api


class DebugDrawExtension(omni.ext.IExt):
    def on_startup(self):
        global _debug_draw_api
        _debug_draw_api = acquire_debug_draw_interface()

    def on_shutdown(self):
        global _debug_draw_api
        release_debug_draw_interface(_debug_draw_api)
        _debug_draw_api = None
