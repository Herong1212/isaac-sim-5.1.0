"""Script to create a viewport stage."""

import carb
import argparse
import asyncio
import omni.usd
from omni.kit import viewport_legacy

async def createViewportAndSetCamera(w, h, x, y, cam):
    await omni.kit.app.get_app().next_update_async()
    viewportFactory = viewport_legacy.get_viewport_interface()
    handle = viewportFactory.create_instance()
    win = viewportFactory.get_viewport_window(handle)
    win.set_window_size(w, h)
    win.set_window_pos(x, y)
    if cam:
        win.set_active_camera(cam)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("width", help="Viewport width.", type=int)
    parser.add_argument("height", help="Viewport height.", type=int)
    parser.add_argument("posx", help="Viewport position - x.", type=int)
    parser.add_argument("posy", help="Viewport position - y.", type=int)
    parser.add_argument("--camera", nargs='?', type=str)

    try:
        options = parser.parse_args()
    except Exception as e:
        carb.log_error(str(e))
        return

    asyncio.ensure_future(createViewportAndSetCamera(options.width, options.height, options.posx, options.posy, options.camera))


main()

