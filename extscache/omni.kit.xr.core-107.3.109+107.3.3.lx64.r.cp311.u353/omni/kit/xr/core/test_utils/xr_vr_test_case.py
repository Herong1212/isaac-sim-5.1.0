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


class XRTestVR(XRTest):
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

    def set_vr_profile_defaults(self, name: str) -> None:
        """
        Setup a test vr profile with tools

        Args:
            name:   name of the profile
        """

        settings = carb.settings.get_settings()

        # Settings normally set when doing XR
        settings.set("/xr/profile/" + name + "/cloudxr/mode", "vr")

        # Default values for navigation
        settings.set("/defaults/xr/profile/" + name + "/system/display", "SimulatedXR")
        settings.set("/defaults/xr/profile/" + name + "/renderQuality", "quality")
        settings.set("/defaults/xr/profile/" + name + "/foveation/mode", "warped")
        settings.set("/defaults/xr/profile/" + name + "/render/resolutionMultiplier", 1.0)
        settings.set("/defaults/xr/profile/" + name + "/refreshRate", 300.0)  # run through test as fast as possible

        # Test Render settings
        settings.set("/defaults/xr/profile/" + name + "/tools/layout", "")
        settings.set("/defaults/xr/profile/" + name + "/gui/layers", [])
        settings.set("/defaults/xr/profile/" + name + "/adjustForUserHeight", False)

    def set_vr_ui_profile_defaults(self, name: str) -> None:

        self.set_vr_profile_defaults(name)

        settings = carb.settings.get_settings()
        settings.set("/defaults/xr/profile/" + name + "/tools/layout", "vr")
        settings.set("/defaults/xr/profile/" + name + "/gui/layers", ["controllers", "tooltips"])
        settings.set("/defaults/xr/profile/" + name + "/tooltips/visible", False)
        settings.set("/defaults/xr/profile/" + name + "/controllers/visible", True)

    def create_test_vr_profile(self, name: str) -> XRProfile:
        """
        Setup a test vr profile with tools for unit/stress testing

        Args:
            name:   name of the profile
        """

        self.set_vr_profile_defaults(name)
        self.set_vr_profile_settings(name)

        return XRCore.get_singleton().ensure_profile(name)

    def create_test_vr_ui_profile(self, name: str) -> XRProfile:
        """
        Setup a test vr profile with tools for unit/stress testing

        Args:
            name:   name of the profile
        """

        self.set_vr_ui_profile_defaults(name)
        self.set_vr_profile_settings(name)

        return XRCore.get_singleton().ensure_profile(name)

    def set_vr_profile_settings(self, name: str):
        """
        Except for profile default settings, this function is used to set (or overwrite) additional profile settings
        specifically when reusing the same profile name but not inherited settings. Ex: omni.kit.xr.abc.TestA and
        omni.kit.xr.abc.TestB are both enabling profile "testvr" but TestB can specify VR_PROFILE_SETTINGS as
        { "foveation/mode": None } to disable foveation which was enabled by TestA

        Args:
            name (str): name of the profile
        """
        if hasattr(self, "VR_PROFILE_SETTINGS") and isinstance(self.VR_PROFILE_SETTINGS, dict):
            settings = carb.settings.get_settings()
            for setting_path, setting_val in self.VR_PROFILE_SETTINGS.items():
                settings.set(f"/xr/profile/{name}/{setting_path}", setting_val)

    async def start_vr_test_profile(self) -> XRProfile:
        """
        Start a mock VR profile
        """

        self.__profiles["testvr"] = self.create_test_vr_profile("testvr")

        # Request to enable a given profile
        self.request_enable_profile("testvr")

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(20)

        # Check that profile was enabled
        self.assertEqual(get_current_xr_profile_name(), "testvr")

        return self.__profiles["testvr"]

    async def start_vr_ui_test_profile(self) -> XRProfile:
        """
        Start a mock VR profile
        """

        self.__profiles["testvrui"] = self.create_test_vr_ui_profile("testvrui")

        # Request to enable a given profile
        self.request_enable_profile("testvrui")

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(20)

        # Check that profile was enabled
        self.assertEqual(get_current_xr_profile_name(), "testvrui")

        return self.__profiles["testvrui"]


class TestVRProfile:
    """
    Helper class invoking starting/stopping vr_test_profile from XRTestVR instance.
    """

    WAIT_ASYNC_TIME = 3

    def __init__(self, test_class_instance: XRTestVR):
        self.test_class_instance = test_class_instance

    async def __aenter__(self) -> XRProfile:
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        vr_test_profile = await self.test_class_instance.start_vr_test_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        return vr_test_profile

    async def __aexit__(self, type, value, traceback):
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        self.test_class_instance.request_disable_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)


class TestVRUIProfile:
    """
    Helper class invoking starting/stopping vr_ui_test_profile from XRTestVR instance.
    """

    WAIT_ASYNC_TIME = 3

    def __init__(self, test_class_instance: XRTestVR):
        self.test_class_instance = test_class_instance

    async def __aenter__(self) -> XRProfile:
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        vr_test_profile = await self.test_class_instance.start_vr_ui_test_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        return vr_test_profile

    async def __aexit__(self, type, value, traceback):
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
        self.test_class_instance.request_disable_profile()
        await self.test_class_instance.wait_post_sync_async(self.WAIT_ASYNC_TIME)
