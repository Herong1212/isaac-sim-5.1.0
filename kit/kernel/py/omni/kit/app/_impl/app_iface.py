__copyright__ = "Copyright (c) 2023-2025, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

# __all__ = ["get_app"]

import asyncio
from functools import lru_cache

import carb.eventdispatcher
import carb.events  # for backwards compatibility

from .._app import *


@lru_cache()
def get_app_interface() -> IApp:
    """Returns cached :class:`omni.kit.app.IApp` interface"""
    return acquire_app_interface()


def get_app() -> IApp:
    """Returns cached :class:`omni.kit.app.IApp` interface. (shorthand)"""
    return get_app_interface()


async def _pre_update_async(
    self, name="omni.kit.app.pre_update_async", order=UPDATE_ORDER_PYTHON_ASYNC_FUTURE_BEGIN_UPDATE
) -> float:
    """Wait for next frame's pre-update of Omniverse Kit. Return delta time in seconds"""

    f = asyncio.Future()

    def on_event(ev: carb.eventdispatcher.Event):
        if not f.done():
            f.set_result(ev["dt"])

    # Previously this used get_update_event_stream(), not the expected get_pre_update_event_stream()
    _ = carb.eventdispatcher.get_eventdispatcher().observe_event(
        order, GLOBAL_EVENT_PRE_UPDATE, on_event, observer_name=name
    )
    return await f


async def _next_update_async(
    self, name="omni.kit.app.next_update_async", order=UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE
) -> float:
    """Wait for next frame's update of Omniverse Kit. Return delta time in seconds"""

    f = asyncio.Future()

    def on_event(ev: carb.eventdispatcher.Event):
        if not f.done():
            f.set_result(ev["dt"])

    _ = carb.eventdispatcher.get_eventdispatcher().observe_event(
        order, GLOBAL_EVENT_UPDATE, on_event, observer_name=name
    )
    return await f


async def _post_update_async(
    self, name="omni.kit.app.post_update_async", order=POST_UPDATE_ORDER_PYTHON_ASYNC_FUTURE
) -> float:
    """Wait for next frame's post-update of Omniverse Kit. Return delta time in seconds"""

    f = asyncio.Future()

    def on_event(ev: carb.eventdispatcher.Event):
        if not f.done():
            f.set_result(ev["dt"])

    _ = carb.eventdispatcher.get_eventdispatcher().observe_event(
        order, GLOBAL_EVENT_POST_UPDATE, on_event, observer_name=name
    )
    return await f


IApp.next_update_async = _next_update_async
IApp.post_update_async = _post_update_async
IApp.pre_update_async = _pre_update_async
