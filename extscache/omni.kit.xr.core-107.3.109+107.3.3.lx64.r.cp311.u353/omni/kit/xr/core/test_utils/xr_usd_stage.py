# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import asyncio
import functools
from typing import Optional, Set

import carb
import omni.usd


class XRUsdStage:
    """
    Helper class encapsulating opening/creating usd stage
    """

    def __init__(self, usd_file_path: Optional[str] = None, keep_stage: Optional[bool] = False) -> None:
        self._usd_file_path = usd_file_path
        self._keep_stage = keep_stage

    async def __aenter__(self):
        ctx = omni.usd.get_context()
        if self._usd_file_path:
            await ctx.open_stage_async(self._usd_file_path)
        else:
            await ctx.new_stage_async()
        await self._wait_for_assets_being_loaded()
        return self

    async def __aexit__(self, type, value, traceback):
        self._stage_sub = None
        if not self._keep_stage:
            await omni.usd.get_context().new_stage_async()

    def __del__(self):
        self._stage_sub = None

    @staticmethod
    def get_layer_names() -> Set[str]:
        """
        Get unique layer names

        Return:
            Set with unique layer names
        """

        names = set()

        stage = omni.usd.get_context().get_stage()

        root_layer = stage.GetRootLayer()
        for path in root_layer.subLayerPaths:
            names.add(path)

        session_layer = stage.GetSessionLayer()
        for path in session_layer.subLayerPaths:
            names.add(path)

        return names

    @staticmethod
    def get_prim_names() -> Set[str]:
        """
        Get unique prim names

        Return:
        Set with unique prim names
        """

        names = set()

        stage = omni.usd.get_context().get_stage()

        for prim in stage.TraverseAll():
            names.add(prim.GetPath())

        return names

    @staticmethod
    def has_xr_gui_prims() -> bool:
        """
        Check if XR related prims exist

        Return:
        True if any prims under "_xr_gui" is found else False
        """

        stage = omni.usd.get_context().get_stage()

        for prim in stage.TraverseAll():
            if str(prim.GetPath()).startswith("/_xr_gui"):
                return True

        return False

    async def _wait_for_assets_being_loaded(self) -> float:

        future: asyncio.Future = asyncio.Future()
        self._cur_count = 0
        MAX_WAIT = 100

        def _on_stage(ev: carb.events.IEvent):
            self._cur_count = self._cur_count + 1
            assets_loading_succeeded = ev.type == int(omni.usd.StageEventType.ASSETS_LOADED)
            assets_loading_failed = (
                ev.type == int(omni.usd.StageEventType.ASSETS_LOAD_ABORTED) or self._cur_count >= MAX_WAIT
            )
            if assets_loading_succeeded or assets_loading_failed:
                self._stage_sub = None
                future.set_result(ev.payload["dt"])
                if assets_loading_failed:
                    carb.log_error("Loading of assets failed inside XRUsdStage")

        self._stage_sub = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(_on_stage, name="USD Stage Subscription")
        )

        return await future


# Wrapper decorator to open/create new UsdStage for entire method (test)
def opened_usd_stage(usd_file_path=None, keep_stage=False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            self = args[0]  # Get the 'self' instance
            async with XRUsdStage(usd_file_path, keep_stage) as usd_stage:
                self.usd_stage = usd_stage
                await func(self)
            self.usd_stage = None

        return wrapper

    return decorator
