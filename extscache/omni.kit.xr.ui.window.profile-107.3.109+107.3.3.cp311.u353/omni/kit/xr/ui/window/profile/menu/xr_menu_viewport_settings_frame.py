# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
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

import carb.settings
import omni.ui as ui
from omni.kit.widget.settings import SettingType

from ..ui.settings_frame import XRSettingsFrame


class XRMenuViewportSettingsFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Viewport Gizmo Settings"

    def build_ui(self):

        # TODO: commented out till we have mechanism to turn on/off camera/light guides (glyphs) without using playingScenario option
        # self.add_setting(
        #     SettingType.BOOL,
        #     "Hide Camera and Light Guides on Start",
        #     self.get_persistent_path() + "viewport/guides/hidden",
        #     tooltip="Hide viewport Camera/Light Guides when profile starts.",
        #     has_reset=False,
        # )

        self.add_setting(
            SettingType.BOOL,
            "Hide Viewport Grid on Start",
            self.get_persistent_path() + "viewport/grid/hidden",
            tooltip="Hide viewport grid when profile starts.",
        )

        self.add_setting(
            SettingType.BOOL,
            "Hide Viewport Selection Outline on Start",
            self.get_persistent_path() + "viewport/outline/hidden",
            tooltip="Hide viewport selection outline when profile starts.",
        )
