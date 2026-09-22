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

import carb
from omni.kit.widget.settings import SettingType

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing what to show in the viewport
#
# Contains:
# - which screen to mirror
# - how to resample the XR display into the viewport
# =======================================================


class XRMenuDesktopDisplayFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Desktop Display Settings"

    def build_ui(self):

        self.add_rebuild_subscription(self.get_persistent_path() + "mirror/displayOutput")

        app_gui_mode_items = {
            "Current": "current",
            "Minimize GUI": "minimized",
            "Full Screen": "fullscreen",
        }
        self.add_setting_combo(
            "Desktop UI Mode",
            self.get_persistent_path() + "app/guiMode",
            app_gui_mode_items,
            tooltip="How to layout the UI of the desktop application in XR mode.\n When there are less windows on the screen the XR application may perform better.",
        )

        display_mode_items = {
            "Left": "left",
            "Right": "right",
            "Both": "both",
            "Viewport": "viewport",
        }
        self.add_setting_combo(
            "Mirror Display Mode",
            self.get_persistent_path() + "mirror/displayMode",
            display_mode_items,
            tooltip="Whether to show left, right or both eyes, or leave the viewport untouched.",
        )

        resampling_items = {
            "Letterbox": "letterbox",
            "Crop": "crop",
            "Stretch": "stretch",
        }
        self.add_setting_combo(
            "Mirror Resizing Option",
            self.get_persistent_path() + "mirror/aspectRatio",
            resampling_items,
            tooltip="How to fit mirror XR displays on the screen.",
        )

        display_items = {
            "Color": "color",
            "Alpha": "alpha",
            "Depth": "depth",
        }
        self.add_setting_combo(
            "Mirror Display Output",
            self.get_persistent_path() + "mirror/displayOutput",
            display_items,
            tooltip="What to show on the desktop application in XR mode.\n When selecting Off a third view will be rendered that may cause a poorer performance in XR.",
        )

        capture_output = carb.settings.get_settings().get(self.get_persistent_path() + "mirror/displayOutput")

        if capture_output == "depth":
            self.add_setting(
                SettingType.FLOAT,
                "Depth Near Plane (in meters)",
                self.get_persistent_path() + "mirror/depthNearPlane",
                0.01,
                50,
                0.01,
                tooltip="Near clipping plane to use for linearized depth display.",
            )

            self.add_setting(
                SettingType.FLOAT,
                "Depth Far Plane (in meters)",
                self.get_persistent_path() + "mirror/depthFarPlane",
                1,
                100,
                1,
                tooltip="Far clipping plane to use for linearized depth display.",
            )

        self.add_setting(
            SettingType.BOOL,
            "Enable XR Status Bar",
            self.get_persistent_path() + "viewport/status/enabled",
            tooltip="Enables XR status bar in the viewport.",
        )
