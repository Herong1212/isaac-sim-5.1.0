import sys
import time
import carb
import carb.eventdispatcher
import asyncio
import argparse
import omni.usd
from pxr import Sdf
from enum import Enum
from copy import deepcopy
from omni.kit.viewport.utility import get_active_viewport_window, create_viewport_window
import omni.renderer_capture

windowCnt = 0
uniqueTickRates = [10, 24, 33, 48, 60, 120]
exitFrameCnt = 200
separateHydraEngine = False
postProcessGraph = False
windows = []
frameNo = {}
cameras = ['/World/Cameras/CameraA', '/World/Cameras/CameraB', '/World/Cameras/CameraC','/World/Cameras/CameraD']
renderProducts = ['/Render/RenderDefault', '/Render/RenderView1', '/Render/RenderView2']
eventSubscription = None
captureFrame = False
renderResolution = None

async def capture_frame():
    global windowCnt
    global eventSubscription
    global windows
    eventSubscription = None

    outFile = carb.settings.get_settings().get("/app/captureFrame/fileName")
    capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
    capture_next_frame(outFile)

    app = omni.kit.app.get_app()
    for _ in range(3):
        await app.next_update_async()

    for window in windows:
        #window.viewport_api._viewport_texture.destroy()
        window.viewport_widget.destroy()
        window.destroy()
        del window
    del windows

    app.post_quit(0)


def on_rendering_event(e: carb.eventdispatcher.Event):
    global captureFrame
    if captureFrame:
        return

    global frameNo
    global windowCnt
    viewId = e["viewport_handle"]
    # Get the minimum frame for the last windowCnt items
    # (This avoids intermediate frames that may have been delivered from a viewport_handle that internally mutated internally)
    frameNo[viewId] = e["frame_number"]
    minFrameRate = min(list(frameNo.values())[-windowCnt:])
    if minFrameRate >= exitFrameCnt:
        captureFrame = True
        asyncio.ensure_future(capture_frame())


def load_callback(result, err):
    if result:
        run_test()
    else:
        carb.log_error("test_multiview.py: usd stage file load failed")
        omni.kit.app.get_app().post_quit(-1)


async def applyCarbSettings():
    try:
        carb.settings.get_settings().set_string("/rtx/rendermode", "RaytracedLighting")
        asyncio.ensure_future(create_viewports())
    except Exception as e:
        carb.log_error("test_multiview.py: applyCarbSettings exception")
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)


async def create_viewports():
    try:
        global windows
        global uniqueTickRates
        global separateHydraEngine
        global postProcessGraph
        global cameras
        global renderResolution

        x_pos = 12
        y_pos = 75

        app = omni.kit.app.get_app()
        usd_context = omni.usd.get_context()

        default_viewport_window = get_active_viewport_window()
        if default_viewport_window:
            default_viewport = default_viewport_window.viewport_api
            # Wait for two frames as original script did that through control-flow in applyCarbSettings => create_viewports
            await usd_context.next_frame_async(default_viewport, n_frames=2)
            # Hide the default Viewport window and make sure it doesn't render
            default_viewport_window.visible = False
            default_viewport.updates_enabled = False
            default_viewport.destroy()
            default_viewport_window.destroy()

        for i in range(len(windows)):
            if i and i%3 == 0:
                x_pos = 12
                y_pos += 312

            hydra_engine_options = {}
            if separateHydraEngine:
                hydra_engine_options['hydra_tick_rate'] = uniqueTickRates[i % len(uniqueTickRates)]

            vp_window = create_viewport_window(name = f"Viewport {i}",
                                               width=300, height=300, position_x=x_pos, position_y=y_pos,
                                               hydra_engine_options=hydra_engine_options)

            vp_window.position_x, vp_window.position_y = x_pos, y_pos
            windows[i] = vp_window

            # Explicitly set resolution based on script arguments
            if renderResolution:
                vp_window.viewport_api.resolution = renderResolution

            if separateHydraEngine:
                # Await one app tick so a render is scheduled
                await app.next_update_async()
                await usd_context.next_frame_async(vp_window.viewport_api)
            x_pos += 312

        await setup_viewport(windows, cameras, separateHydraEngine, postProcessGraph)

    except Exception as e:
        carb.log_error("test_multiview.py: create_viewports exception")
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)


async def setup_viewport(windows, cameras, separateHydraEngine, postProcessGraph):
    try:
        for i in range(len(windows)):
            viewport = windows[i].viewport_api
            if postProcessGraph:
                viewport.render_product_path = renderProducts[i % len(renderProducts)]
            else:
                viewport.camera_path = cameras[i % len(cameras)]
            if separateHydraEngine:
                await viewport.usd_context.next_frame_async(viewport)
    except Exception as e:
        carb.log_error("test_multiview.py: set_cameras exception")
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)


def run_test():
    asyncio.ensure_future(applyCarbSettings())


def main():
    global windows
    global windowCnt
    global postProcessGraph
    global eventSubscription
    global separateHydraEngine
    global renderResolution

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to USD stage.")
    parser.add_argument("--windowCnt", type=int, required=True, help="Number of viewports to create")
    parser.add_argument('--separateHydraEngine', dest='separateHydraEngine', action='store_true')
    parser.add_argument('--no-separateHydraEngine', dest='separateHydraEngine', action='store_false')
    parser.set_defaults(separateHydraEngine=False)
    parser.add_argument('--postProcessGraph', dest='postProcessGraph', action='store_true')
    parser.add_argument('--no-postProcessGraph', dest='postProcessGraph', action='store_false')
    parser.set_defaults(postProcessGraph=False)

    settings = carb.settings.get_settings()
    resX, resY = settings.get("/app/window/width"), settings.get("/app/window/height")
    if resX and resY:
        renderResolution = (resX, resY)
    
    try:
        options = parser.parse_args()
        windowCnt = options.windowCnt
        windows = [None] * windowCnt
        context = omni.usd.get_context()
        eventSubscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
            on_event=on_rendering_event,
            observer_name="test_multiview"
        )
        postProcessGraph = options.postProcessGraph
        separateHydraEngine = options.separateHydraEngine
        if separateHydraEngine:
            for i in range(windowCnt):
                omni.usd.create_hydra_engine("rtx", context)
        context.open_stage_with_callback(options.path, load_callback)
    except Exception as e:
        carb.log_error("test_multiview.py: main exception")
        carb.log_error(str(e))
        omni.kit.app.get_app().post_quit(-1)

main()
