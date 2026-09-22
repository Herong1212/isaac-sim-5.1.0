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

import platform

import carb
import omni.ui as ui

from ..ui.settings_frame import XRSettingsFrame
from .xr_menu_openxr_utils import get_openxr_runtime


class XRMenuOpenXRInfo(XRSettingsFrame):
    def get_frame_name(self):
        return "Information"

    def build_ui(self):
        self.add_rebuild_subscription(self.get_non_persistent_path() + "enabled")
        self.add_rebuild_subscription(self.get_non_persistent_path() + "quadview/active")
        self.add_rebuild_subscription(self.get_non_persistent_path() + "eyetracking/active")

        with ui.VStack():
            self._add_text(f"OpenXR Active Runtime: {get_openxr_runtime()}")
            self.add_info(
                "OpenXR Runtime Version",
                self.get_non_persistent_path() + "openxr/runtime/version",
            )
            self.add_info(
                "OpenXR API Version",
                self.get_non_persistent_path() + "openxr/api/version",
            )

            ui.Spacer(height=15)
            ui.Line()
            ui.Spacer(height=15)

            openxr_running = carb.settings.get_settings().get(self.get_non_persistent_path() + "enabled")

            if openxr_running:
                self.add_info_bool(
                    "Quadview",
                    self.get_non_persistent_path() + "quadview/active",
                    "Active",
                    "Not Used",
                )
                self.add_info_bool(
                    "Eyetracking",
                    self.get_non_persistent_path() + "eyetracking/active",
                    "Active",
                    "Not Used",
                )
            else:
                self.add_info_bool(
                    "Eyetracking",
                    self.get_non_persistent_path() + "openxr/eyetracking/available",
                    "Detected",
                    "N/A",
                )
