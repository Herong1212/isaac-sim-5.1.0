
import argparse
import asyncio
import carb
import carb.eventdispatcher
import omni.usd
import omni.timeline
import omni.kit.app
from omni.kit.viewport.utility import get_active_viewport_window

on_rendering_sub = None
capture = True
timeline = None
frames = None
prefix = None
worker = False
fps = 24.0
maxFrame = 600

def captureFrame (filename_prefix, frame):
    filename = filename_prefix + frame + ".png"
    capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
    capture_next_frame(filename)
    carb.log_info("Saving " + filename)

async def shutdown():
    global on_rendering_sub
    omni.usd.get_context().close_stage(None)
    omni.kit.app.get_app().post_uncancellable_quit(0)
    on_rendering_sub = None

def on_rendering_event(e: carb.eventdispatcher.Event):
    global capture
    global maxFrame
    global timeline

    frame_number = e["frame_number"]

    if not worker:
        if frame_number > maxFrame:
           asyncio.ensure_future(shutdown())

    if capture:
        if frame_number == frames[0]:
            captureFrame(prefix, str(frame_number))
            if not worker and frames[1] != -1: # Master advances animation
                timeline.set_current_time(float(frames[1] / fps))
            if frames[1] == -1: # Single frame case (multi-process rendering)
                capture = False
        elif frame_number == frames[1]:
            captureFrame(prefix, str(frame_number))
            if not worker: # Master advances animation
                timeline.set_current_time(float(frames[2] / fps))
        elif frame_number == frames[2]:
            captureFrame(prefix, str(frame_number))
            capture = False

def run(args):
    global frames
    global prefix
    global worker
    global on_rendering_sub
    global timeline

    frames = args.frames
    prefix = args.prefix
    worker = args.worker
    usdContext = omni.usd.get_context()

    on_rendering_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
        event_name=usdContext.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
        on_event=on_rendering_event,
        observer_name="multi_process_capture"
    )

    if not worker:
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_time_codes_per_second(fps)
        timeline.set_start_time(0.0)
        timeline.set_current_time(float(frames[0] / fps))
        viewport_window = get_active_viewport_window()
        viewport_window.width = 360
        viewport_window.height = 360

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", help="Set to True if this script is called by a worker. \
                        When True cannot be used with --filename", type=bool, default=False)
    parser.add_argument("prefix", help="Filename prefix for the image(s) to capture.", type=str)
    parser.add_argument("frames", help="Three frames to capture.", type=int, nargs=3)

    run(parser.parse_args())