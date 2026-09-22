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

import carb
from omni.kit.xr.core import XRCore, XRCoreEventType, XRProfile


def get_current_profile() -> XRProfile:
    """
    Get the current profile
    """

    return XRCore.get_singleton().get_current_xr_profile()


def get_current_xr_profile_name() -> str:
    """
    Get the current profile name
    """

    return XRCore.get_singleton().get_current_xr_profile_name()


class EnabledXRProfile:
    """
    Helper class encapsulating enabling/disabling of XR profile
    """

    def __init__(self, profile_name: str, frames_to_wait: int = 3):
        if profile_name is None or not profile_name:
            raise ValueError("Profile name string is None or empty")

        self.profile_name = profile_name
        self.frames_to_wait = frames_to_wait

    async def __aenter__(self):
        XRCore.get_singleton().request_enable_profile(self.profile_name)
        await self._wait_post_sync_async(self.frames_to_wait)

    async def __aexit__(self, type, value, traceback):
        XRCore.get_singleton().request_disable_profile()
        await self._wait_post_sync_async(self.frames_to_wait)

    def __del__(self):
        self._sub_profile_change = None
        self._sub_post_sync = None

    async def _wait_post_sync_async(self, count) -> None:
        """
        Wait several frames
        """

        future: asyncio.Future = asyncio.Future()
        self._cur_count = 0

        def on_post_sync(ev: carb.events.IEvent):
            self._cur_count += 1
            if self._cur_count >= count:
                future.set_result(True)

        self._sub_post_sync = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.post_sync_update, on_post_sync, name="Post Sync")
        )

        await future

        self._sub_post_sync = None

        return
