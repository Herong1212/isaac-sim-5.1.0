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

from typing import Dict, Optional

import carb
from omni.kit.xr.core import XRCore, XRProfile

from .xr_profile import get_current_xr_profile_name
from .xr_test import XRTest


class XRTestTablet(XRTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__profiles: Dict[str, Optional[XRProfile]] = None

    async def setUp(self):
        """
        Setup: Ensure we have a clean scene and wait
        a number of frames to clear buffers.
        """

        await super().setUp()
        self.__profiles = {}

    async def tearDown(self):
        """
        Disable any outstanding profile and wait
        some mor cycles to clear on going processes
        """

        self.__profiles = {}

        await super().tearDown()

    def create_tablet_profile(self, name: str) -> XRProfile:
        """
        Setup a test vr profile with tools

        Args:
            name:   name of the profile
        """

        if name in self.__profiles:
            return

        settings = carb.settings.get_settings()

        # Settings normally set when doing XR
        settings.set("/xr/profile/" + name + "/navigationMode", "default")
        settings.set("/xr/profile/" + name + "/cloudxr/mode", "tablet")

        # Default values for navigation
        settings.set("/defaults/xr/profile/" + name + "/navigationUpdateTarget", "physicalWorldTransform")
        settings.set("/defaults/xr/profile/" + name + "/system/display", "SimulatedXR")
        settings.set("/defaults/xr/profile/" + name + "/system/displayMode", "tabletAR")

        settings.set("/defaults/xr/profile/" + name + "/renderQuality", "quality")
        settings.set("/defaults/xr/profile/" + name + "/foveation/mode", "warped")
        settings.set("/defaults/xr/profile/" + name + "/render/resolutionMultiplier", 0.5)

        # Test Render settings
        settings.set("/defaults/xr/profile/" + name + "/tools/layout", "")
        settings.set("/defaults/xr/profile/" + name + "/gui/layers", [])
        settings.set("/defaults/xr/profile/" + name + "/adjustForUserHeight", False)

        self.__profiles[name] = XRCore.get_singleton().ensure_profile(name)
        return self.__profiles[name]

    # TODO: remove that method, it is added because testvr is not a real profile and does not
    # invoke '_update_settings' which does the same logic inside xr_profile_common.py
    def update_viewport_gizmos(self):
        settings = carb.settings.get_settings()
        hideGrid: bool = settings.get("/xr/profile/" + get_current_xr_profile_name() + "/viewport/grid/hidden")
        settings.set("/app/viewport/grid/enabled", not hideGrid)

        hideOutline: bool = settings.get("/xr/profile/" + get_current_xr_profile_name() + "/viewport/outline/hidden")
        settings.set("/app/viewport/outline/enabled", not hideOutline)

    def create_test_tablet_profile(self, name: str) -> XRProfile:
        """
        Setup a test vr profile with tools for unit/stress testing

        Args:
            name:   name of the profile
        """

        profile = self.create_tablet_profile(name)

        settings = carb.settings.get_settings()
        settings.set("/xr/profile/" + name + "/render/resolutionMultiplier", 0.5)

        return profile

    def create_perf_tablet_profile(self, name: str) -> XRProfile:
        """
        Setup a test vr profile with tools for performance test

        Args:
            name:   name of the profile
        """

        profile = self.create_tablet_profile(name)

        settings = carb.settings.get_settings()
        settings.set("/xr/profile/" + name + "/render/resolutionMultiplier", 1.0)

        return profile

    async def start_tablet_test_profile(self) -> XRProfile:
        """
        Start a mock VR profile
        """

        await self.wait_post_sync_async(50)

        self.create_test_tablet_profile("testtablet")

        # Request to enable a given profile
        self.request_enable_profile("testtablet")

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(200)

        # Check that profile was enabled
        self.assertEqual(get_current_xr_profile_name(), "testtablet")

        return self.__profiles["testtablet"]


class TestTabletProfile:
    """
    Helper class invoking starting/stopping vr_test_profile from XRTestVR instance.
    """

    WAIT_ASYNC_TIME = 3

    def __init__(self, test_class_instance: XRTestTablet):
        self.test_class_instance = test_class_instance

    async def __aenter__(self) -> XRProfile:
        vr_test_profile = await self.test_class_instance.start_tablet_test_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        return vr_test_profile

    async def __aexit__(self, type, value, traceback):
        self.test_class_instance.request_disable_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
