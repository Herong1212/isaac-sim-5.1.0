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

# =======================================================
# Menu component describing how keyboard/mouse navigation
# should be done in XR
#
# Contains:
# - definitions for Anchor (not using Anchor panel)
# - switches for whether keyboard/mouse navigation is enabled
# - Whether anchor is moved or transform on top of anchor is
#   moved when moving through the scene
# =======================================================


class XRMenuNavigationFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Navigation Settings"

    def build_ui(self):

        self.add_rebuild_subscription(self.get_persistent_path() + "anchorMode")
        self.add_rebuild_subscription(self.get_scene_persistent_path() + "enableCameraOutput")

        anchorMode = carb.settings.get_settings().get(self.get_persistent_path() + "anchorMode")

        def reset_anchor():
            carb.settings.get_settings().set("/xr/anchor/reset", True)

        with ui.HStack():
            ui.Spacer()
            ui.Button(
                "Recenter",
                clicked_fn=reset_anchor,
                width=160,
                height=28,
                style={"border_radius": 4},
                tooltip="Click here to recenter experience.\n This will reapply initial settings for selected anchor.",
            )
            ui.Spacer(width=35)

        ui.Spacer(height=10)
        ui.Line()
        ui.Spacer(height=5)

        anchormode_items = {"Custom USD Anchor": "custom anchor", "Scene Origin": "scene origin"}

        if self._profile.get_name() != "tabletar":
            anchormode_items["Active Camera"] = "active camera"

        self.add_setting_combo(
            "Physical World USD Anchor",
            self.get_persistent_path() + "anchorMode",
            anchormode_items,
            tooltip="How to link physical world to the virtual world.",
        )

        customAnchorPath = self.get_scene_persistent_path() + "customAnchor"

        if anchorMode == "custom anchor":
            self.add_setting(
                "PATH",
                "Path For Custom USD Anchor",
                customAnchorPath,
                tooltip="Which Usd Prim to use as the anchor for the physical world.",
            )

        self.add_setting(
            SettingType.BOOL,
            "Enable Mouse/Keyboard",
            self.get_persistent_path() + "enableNavigationControls",
            tooltip="Enable moving through the scene by keyboard like in the editor.",
        )

        self.add_setting(
            SettingType.BOOL,
            "Floor-aligned movements",
            self.get_persistent_path() + "floorAlignedNavigation",
            tooltip="Flying through the virtual space is along the floor to avoid disorientation.",
        )

        self.add_setting(
            SettingType.BOOL,
            "Disable Leveled Physical World",
            self.get_persistent_path() + "overrideFloorAlignedAnchor",
            tooltip="When matching XR display with USD Primitive disable\n the correction to make user be aligned with the floor in the Usd Stage.",
        )

        if self._profile.get_name() == "vr":

            self.add_setting(
                SettingType.BOOL,
                "Adjust for User Height",
                self.get_persistent_path() + "adjustForUserHeight",
                tooltip="Adjust for user height when entering a scene or changing camera.",
            )

            self.add_setting(
                SettingType.FLOAT,
                "Max Teleport Arc Height (meters)",
                self.get_persistent_path() + "teleport/arc/maxHeight",
                1.0,
                50.0,
                1.0,
                tooltip="Maximum height for teleporter arc. The higher it can go the further one can leap,\n but this maybe harder in tight spaces.",
            )

            self.add_setting(
                SettingType.FLOAT,
                "Controller Navigation Speed",
                self.get_persistent_path() + "navigation/speed",
                0.1,
                15.0,
                0.1,
                tooltip="Speed with which the controller lets you fly through the world.",
            )
