__all__ = ["start_replay_if_enabled", "stop_replay_service"]

import asyncio
import threading

import carb
from omni.kit.xr.core import XRCore, XRCoreEventType, XRProfile

from .._xr_xcr import XCRReplayAPI

xcr_api = XCRReplayAPI()


def start_replay_if_enabled(xr_profile: XRProfile):
    """Play the captured replay if replay file is selected on UI. This function creates an event loop in another thread which can
        avoid blocking main thread (UI thread) and also subscribe "pre_sync_update" event in a new event loop.

    Args:
        xr_profile (XRProfile): current profile
    """
    carb_settings = carb.settings.get_settings()
    is_replay_enabled = carb_settings.get("/xr/system/openxr/xcr/replay/enabled")
    replay_file_path = carb_settings.get("/xr/system/openxr/xcr/replay/replayFile")
    current_system = carb_settings.get(xr_profile.get_persistent_path() + "system/display")
    if is_replay_enabled and current_system == "OpenXR" and replay_file_path:
        carb.log_info(f"replay file is selected: {replay_file_path}")
        carb_settings.set("/xr/raycastsDeterministic", True)

        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=loop.run_forever, name="Async Runner", daemon=True)
        thread.start()
        asyncio.run_coroutine_threadsafe(start_replay(replay_file_path, loop, xr_profile), loop)
    else:
        carb.log_info("XCR Replay is disabled or replay file is not selected")


def stop_replay_service(xr_profile: XRProfile):
    carb_settings = carb.settings.get_settings()
    replay_file_path = carb_settings.get("/xr/system/openxr/xcr/replay/replayFile")
    current_system = carb_settings.get(xr_profile.get_persistent_path() + "system/display")
    if current_system == "OpenXR" and replay_file_path:
        try:
            xcr_api.stop_replay_service_immediately()
        except Exception as e:
            if "XCR Replay Service is not running" in str(e):
                carb.log_warn("No need to stop XCR Replay Service ")
            else:
                raise e


async def start_replay(replay_file_path: str, loop: asyncio.events.AbstractEventLoop, xr_profile: XRProfile):
    """This coroutine start XCR replay service and change replay frame by frame when event "pre_sync_update" is fired
    At the end of replay, this coroutine cleans up event subscription and event loop, and finally stop XR profile

    Args:
        replay_file_path (str): path to captured replay file
        loop (asyncio.events.AbstractEventLoop): event loop for receiving pre_sync_update and change replay frame
        xr_profile (XRProfile): current profile

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    future: asyncio.Future = asyncio.Future()
    try:
        xcr_api.start_replay_service(replay_file_path)
    except Exception as e:
        if "XCR Replay Service is already running" in str(e):
            xcr_api.stop_replay_service_immediately()
            xcr_api.start_replay_service(replay_file_path)
        else:
            future.set_exception(e)
            raise e

    frame_index = 0
    frames_count = xcr_api.get_replay_frame_count()

    def set_xcr_frame(_: carb.events.IEvent):
        nonlocal frame_index
        if frame_index < frames_count:
            try:
                xcr_api.set_replay_frame(frame_index)
                frame_index = frame_index + 1
                return
            except RuntimeError:
                # XCR Replay Service is not running, unsubscribe "pre_sync_update" and complete the event loop
                carb.log_warn(
                    "XCR service is not running but set_xcr_frame is continuously triggered by pre_sync_update"
                )

        if not future.done() and not future.cancelled():
            sub_pre_sync.unsubscribe()
            loop.call_soon_threadsafe(future.set_result, "Done")  # unblock "await future"

    sub_pre_sync = (
        XRCore.get_singleton()
        .get_message_bus()
        .create_subscription_to_pop_by_type(
            XRCoreEventType.pre_sync_update,
            set_xcr_frame,
            name="set_xcr_frame",
            order=-1,
        )
    )
    result = await future
    carb_settings = carb.settings.get_settings()
    carb_settings.set(xr_profile.get_non_persistent_path() + "enabled", False)
    return result
