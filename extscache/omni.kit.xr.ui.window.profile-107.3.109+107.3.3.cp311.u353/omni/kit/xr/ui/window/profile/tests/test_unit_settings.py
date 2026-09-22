# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
from omni.kit.xr.core import XRCore
from omni.kit.xr.core.test_utils import XRTest
from omni.kit.xr.ui.window.profile import XRSettingsFrame
from omni.kit.xr.ui.window.profile.menu import (
    XRMenuAnchorFrame,
    XRMenuClippingPlanesFrame,
    XRMenuDesktopDisplayFrame,
    XRMenuEyeTrackingFrame,
    XRMenuFoveationSettingsFrame,
    XRMenuGeneralFrame,
    XRMenuMatteObjectFrame,
    XRMenuNavigationFrame,
    XRMenuOpenXRInfo,
    XRMenuOpenXRSetupInstructions,
    XRMenuOutputFrame,
    XRMenuScalingFrame,
    XRMenuSimulatedXRInfo,
    XRMenuSimulationFrame,
    XRMenuSimulationStereoFrame,
    XRMenuSimulationTabletFrame,
    XRMenuSystemInfo,
    XRMenuViewportSettingsFrame,
    XRMenuXCRFrame,
    XRMenuXRDepthFrame,
)


class TestSettings(XRTest):
    @classmethod
    def setUpClass(cls):
        cls.settings = carb.settings.get_settings()
        cls.settings.set("/xr/profile/vr/system/display", "SimulatedXR")
        cls.frames: [XRSettingsFrame] = []

    async def setUp(self):
        await super().setUp()
        await self.new_stage_async()
        await self.wait_post_sync_async(40)

        self.request_enable_profile("vr")
        self.profile = XRCore.get_singleton().get_profile("vr")
        self.config = {
            "render_quality_items": ["low", "mid", "hi"],
            "show_selected_output_plugin": True,
            "show_resolution_multiplier": True,
            "show_tooltips": True,
        }

    @classmethod
    def tearDownClass(cls):
        for frame in cls.frames:
            frame.destroy()
        cls.frames = []

    def build_frame(self, frame):
        frame.build_ui()
        self.frames.append(frame)

    def enable_quadview(self):
        self.settings.set(self.profile.get_persistent_path() + "quadview/enabled", True)
        self.settings.set(self.profile.get_non_persistent_path() + "quadview/active", True)

    async def test_all(self):
        await self.__test_set_setting()
        await self.__test_menu_anchor_frame()
        await self.__test_menu_clipping_planes_frame()
        await self.__test_menu_desktop_display_frame()
        await self.__test_menu_eye_tracking_frame()
        await self.__test_menu_foveation_settings_frame()
        await self.__test_xr_menu_general_frame()
        await self.__test_xr_menu_matte_object_frame()
        await self.__test_menu_navigation_frame()
        await self.__test_menu_openxr_info()
        await self.__test_menu_openxr_setup_instructions()
        await self.__test_menu_xcr_frame()
        await self.__test_menu_output_frame()
        await self.__test_menu_scaling_frame()
        await self.__test_menu_simulatedxr_info()
        await self.__test_menu_simulation_frame()
        await self.__test_menu_simulation_stereo_frame()
        await self.__test_menu_simulation_tablet_frame()
        await self.__test_menu_system_info()
        await self.__test_menu_viewport_settings_frame()
        await self.__test_menu_xrdepth_frame()

    async def __test_set_setting(self):
        path = self.profile.get_non_persistent_path() + "foveation/showArea"
        self.settings.set_bool(path, True)
        self.assertTrue(self.settings.get(path))

    async def __test_menu_anchor_frame(self):
        self.build_frame(XRMenuAnchorFrame(profile=self.profile))

    async def __test_menu_clipping_planes_frame(self):
        self.build_frame(XRMenuClippingPlanesFrame(profile=self.profile))

    async def __test_menu_desktop_display_frame(self):
        self.build_frame(XRMenuDesktopDisplayFrame(profile=self.profile))
        self.enable_quadview()
        self.build_frame(XRMenuDesktopDisplayFrame(profile=self.profile))

    async def __test_menu_eye_tracking_frame(self):
        self.build_frame(XRMenuEyeTrackingFrame(profile=self.profile))

    async def __test_menu_foveation_settings_frame(self):
        self.settings.set(self.profile.get_persistent_path() + "render/resolutionMultiplier", 1.1)
        self.settings.set(self.profile.get_non_persistent_path() + "foveation/showArea", True)
        self.settings.set(self.profile.get_persistent_path() + "foveation/mode", "none")
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

        self.settings.set(self.profile.get_persistent_path() + "foveation/mode", "warped")
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

        self.settings.set(self.profile.get_persistent_path() + "foveation/mode", "inset")
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

        self.enable_quadview()

        self.settings.set(
            self.profile.get_persistent_path() + "quadview/foveation/mode",
            "render_quadview",
        )
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

        self.settings.set(
            self.profile.get_persistent_path() + "quadview/foveation/mode",
            "render_warped_quadview",
        )
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

        self.settings.set(
            self.profile.get_persistent_path() + "quadview/foveation/mode",
            "stereo_warped_to_quadview",
        )
        self.build_frame(XRMenuFoveationSettingsFrame(profile=self.profile))

    async def __test_xr_menu_general_frame(self):
        self.build_frame(XRMenuGeneralFrame(profile=self.profile, config=self.config))
        self.enable_quadview()
        self.config["show_resolution_multiplier"] = False
        self.build_frame(XRMenuGeneralFrame(profile=self.profile, config=self.config))

    async def __test_xr_menu_matte_object_frame(self):
        self.build_frame(XRMenuMatteObjectFrame(profile=self.profile))

    async def __test_menu_navigation_frame(self):
        self.settings.set(self.profile.get_non_persistent_path() + "teleport/enabled", True)
        self.settings.set(self.profile.get_persistent_path() + "anchorMode", "custom anchor")
        self.settings.set(self.profile.get_scene_persistent_path() + "enableCameraOutput", True)
        self.build_frame(XRMenuNavigationFrame(profile=self.profile, config=self.config))

    async def __test_menu_openxr_info(self):
        self.build_frame(XRMenuOpenXRInfo(profile=self.profile, config=self.config))
        self.settings.set(self.profile.get_non_persistent_path() + "enabled", True)
        self.build_frame(XRMenuOpenXRInfo(profile=self.profile, config=self.config))

    async def __test_menu_openxr_setup_instructions(self):
        self.build_frame(XRMenuOpenXRSetupInstructions(profile=self.profile, config=self.config))

    async def __test_menu_xcr_frame(self):
        self.build_frame(XRMenuXCRFrame(profile=self.profile, config=self.config))

    async def __test_menu_output_frame(self):
        self.build_frame(XRMenuOutputFrame(profile=self.profile, config=self.config))

    async def __test_menu_scaling_frame(self):
        self.build_frame(XRMenuScalingFrame(profile=self.profile, config=self.config))

    async def __test_menu_simulatedxr_info(self):
        self.build_frame(XRMenuSimulatedXRInfo(profile=self.profile, config=self.config))

    async def __test_menu_simulation_frame(self):
        self.build_frame(XRMenuSimulationFrame(profile=self.profile, config=self.config))
        self.settings.set(self.profile.get_persistent_path() + "simulatedxr/depth/enabled", True)
        self.build_frame(XRMenuSimulationFrame(profile=self.profile, config=self.config))

    async def __test_menu_simulation_stereo_frame(self):
        self.build_frame(XRMenuSimulationStereoFrame(profile=self.profile, config=self.config))
        self.enable_quadview()
        self.build_frame(XRMenuSimulationStereoFrame(profile=self.profile, config=self.config))

    async def __test_menu_simulation_tablet_frame(self):
        self.build_frame(XRMenuSimulationTabletFrame(profile=self.profile, config=self.config))

    async def __test_menu_system_info(self):
        self.settings.set(self.profile.get_persistent_path() + "system/display", "OpenXR")
        self.build_frame(XRMenuSystemInfo(profile=self.profile, config=self.config))
        self.settings.set(self.profile.get_persistent_path() + "system/display", "SimulatedXR")
        self.build_frame(XRMenuSystemInfo(profile=self.profile, config=self.config))

    async def __test_menu_viewport_settings_frame(self):
        self.build_frame(XRMenuViewportSettingsFrame(profile=self.profile, config=self.config))

    async def __test_menu_xrdepth_frame(self):
        self.build_frame(XRMenuXRDepthFrame(profile=self.profile))
