# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .._usd import *
from .api import *
from .utils import *
from .layer_utils import *
from .timesample_utils import *
from .watcher import UsdWatcher, get_watcher
from .transform_helper import TransformHelper
from .prim_lists import get_geometry_standard_prim_list, get_light_prim_list

import asyncio
import carb
import carb.eventdispatcher
import omni.ext
import omni.kit.app


# Watcher is singleton. Call destroy explicitly to clean up subscriptions.
class UsdExtension(omni.ext.IExt):
    """omni.usd extension class."""

    async def __init_stage_event(self, app):
        app.delay_app_ready("omni.usd")
        await app.next_update_async()

        settings = carb.settings.get_settings()

        # Check if user or app launched with --/app/content/usdFile=""
        # usd_file = settings.get("/app/content/usdFile")
        # if usd_file:
        #     carb.log_info(f"Opening '{usd_file}'")
        #     await self.__default_context.open_stage_async(usd_file)
        #     self.__init_task = None
        #     return

        if self.__default_context.get_stage():
            self.__clear_history()

        if settings.get("/app/content/emptyStageOnStart"):
            if self.__default_context.get_stage_state() == StageState.CLOSED:
                try:
                    import omni.kit.stage_template.core

                    is_ready = False
                    def on_new_stage(result, error):
                        nonlocal is_ready
                        is_ready = True

                    omni.kit.stage_template.core.new_stage_with_callback(on_new_stage_fn=on_new_stage, template=None)

                    # Ensure APP_READY is released after stage created.
                    while not is_ready:
                        app.delay_app_ready("omni.usd")
                        await app.next_update_async()
                except ModuleNotFoundError:
                    self.__default_context.new_stage()

        self.__init_task = None

    def __clear_history(self):
        import omni.kit.undo

        omni.kit.undo.clear_history()
        omni.kit.undo.clear_stack()

    def __on_stage_opened(self):
        self.__clear_history()

        # Only attach stage if it's instanced by other exts.
        if UsdWatcher._is_instantiated():
            get_watcher()._attach_stage(self.__default_context.get_stage())

        self.__init_task = None

    def __on_stage_closing(self):
        self.__clear_history()

        # Only detach stage if it's instanced by other exts.
        if UsdWatcher._is_instantiated():
            get_watcher()._detach_stage()

        self.__init_task = None

    def on_startup(self):
        # Ensure default context is created.
        omni.usd.create_context()
        self.__default_context = omni.usd.get_context()

        self.__stage_event_sub = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.usd.impl.UsdExtension",
                event_name=self.__default_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self.__on_stage_opened()),
                (omni.usd.StageEventType.CLOSING, lambda _: self.__on_stage_closing()),
            )
        ]

        # delay init_stage_event as it shouldn't trigger before tests and around "app started"
        # OM-52800: Delay app ready to make sure stage is initialized before app ready.
        app = omni.kit.app.get_app()
        app.delay_app_ready("omni.usd")
        self.__init_task = asyncio.ensure_future(self.__init_stage_event(app))

    def on_shutdown(self):
        self.__stage_event_sub = None
        self.__default_context = None
        if self.__init_task:
            self.__init_task.cancel()
            self.__init_task = None

        if UsdWatcher._is_instantiated():
            get_watcher().destroy()

        omni.usd.destroy_context()
        omni.usd.shutdown_usd()


def _get_stage(self):
    """Gets current opened :class:`pxr.Usd.Stage`"""

    # This function connects `omni.usd.UsdContext` pybind11 python bindings with Pixar's Usd bindings.
    # The UsdStage object is stored by C++ code inside of Usd Utils cache under some id.
    # We get the id from `omni.usd.UsdContext` interface and use it to retrieve UsdStage from Usd Utils.
    from pxr import Usd, UsdUtils

    id = self.get_stage_id()
    cache = UsdUtils.StageCache.Get()
    return cache.Find(Usd.StageCache.Id.FromLongInt(id))


async def _next_frame_async(self, viewport = None, n_frames: int = 1) -> None:
    """Wait for an amount of frame complete events from Kit, possibly targeting a specific viewport."""

    f = asyncio.Future()

    def on_event(e: carb.eventdispatcher.Event):
        # If a Viewport was given, then the new frame must be for it,
        # otherwise any frame delivered is ok.
        vp_handle = viewport.frame_info.get('viewport_handle', None) if viewport else None
        frame_handle = e["viewport_handle"] if viewport else None
        if vp_handle == frame_handle:
            # Wait for any additional frames requested
            nonlocal n_frames
            if n_frames <= 1:
                if not f.done():
                    f.set_result(None)
            else:
                n_frames -= 1

    sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
        event_name=self.stage_rendering_event_name(StageRenderingEventType.NEW_FRAME, True),
        on_event=on_event,
        observer_name="omni.usd._next_frame_async"
    )
    return await f


UsdContext.next_usd_async = _next_frame_async
UsdContext.next_frame_async = _next_frame_async

UsdContext.get_stage = _get_stage

# Deprecated functions
UsdContext.get_stage_event_stream = carb.deprecated("Use Events 2.0")(UsdContext.get_stage_event_stream)
UsdContext.get_rendering_event_stream = carb.deprecated("Use Events 2.0")(UsdContext.get_rendering_event_stream)
