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
import omni.ui
from omni.kit.widget.settings import SettingType

from .xr_menu_simulation_frame import XRMenuSimulationFrame


class XRMenuSimulationStereoFrame(XRMenuSimulationFrame):
    def get_frame_name(self):
        return "Simulation Settings"

    def build_ui(self):
        super().build_ui()
        self.add_rebuild_subscription(self.get_persistent_path() + "simulatedxr/quadview/enabled")

        self._ui_subsection_separation()

        self.add_setting(
            SettingType.BOOL,
            "Quadview Enabled",
            self.get_persistent_path() + "simulatedxr/quadview/enabled",
            tooltip="Whether quad view mode is enabled",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Inter Pupil Distance (m)",
            self.get_persistent_path() + "simulatedxr/stereo/ipd",
            0.05,
            0.08,
            0.001,
            tooltip="Distance to simulate between pupils",
        )

        quadview_enabled = carb.settings.get_settings().get(self.get_persistent_path() + "simulatedxr/quadview/enabled")

        if not quadview_enabled:
            self._ui_subsection_separation()
            omni.ui.Label("Stereo Settings")
            omni.ui.Spacer(height=5)

            self.add_setting(
                SettingType.INT2,
                "Resolution",
                self.get_persistent_path() + "simulatedxr/stereo/resolution",
                300,
                8192,
                100,
                labels=[("W", 0xFF353585), ("H", 0xFF853331)],
                tooltip="Simulated resolution for both left and right eye",
            )

            omni.ui.Spacer(height=15)

            self.add_setting(
                SettingType.DOUBLE2,
                "Left Horizontal FOV Range",
                self.get_persistent_path() + "simulatedxr/stereo/left/fovX",
                -3,
                3,
                0.1,
                labels=[("L", 0xFF353585), ("R", 0xFF853331)],
                tooltip="Left and right vertical field of view tangents for left eye",
            )

            self.add_setting(
                SettingType.DOUBLE2,
                "Left Vertical FOV Range",
                self.get_persistent_path() + "simulatedxr/stereo/left/fovY",
                -3,
                3,
                0.1,
                labels=[("B", 0xFF353585), ("T", 0xFF853331)],
                tooltip="Top and bottom vertical field of view tangents for left eye",
            )

            omni.ui.Spacer(height=15)

            self.add_setting(
                SettingType.DOUBLE2,
                "Right Horizontal FOV Range",
                self.get_persistent_path() + "simulatedxr/stereo/right/fovX",
                -3,
                3,
                0.1,
                labels=[("L", 0xFF353585), ("R", 0xFF853331)],
                tooltip="Left and right vertical field of view tangents for right eye",
            )

            self.add_setting(
                SettingType.DOUBLE2,
                "Right Vertical FOV Range",
                self.get_persistent_path() + "simulatedxr/stereo/right/fovY",
                -3,
                3,
                0.1,
                labels=[("B", 0xFF353585), ("T", 0xFF853331)],
                tooltip="Top and bottom vertical field of view tangents for right eye",
            )

        else:
            self._ui_subsection_separation()
            omni.ui.Label("Quadview Settings")
            omni.ui.Spacer(height=5)

            self.add_setting(
                SettingType.INT2,
                "Background Resolution",
                self.get_persistent_path() + "simulatedxr/quadview/background/resolution",
                1024,
                8192,
                100,
                labels=[("W", 0xFF353585), ("H", 0xFF853331)],
                tooltip="Resolution to simulate for background rendering",
            )

            self.add_setting(
                SettingType.INT2,
                "Inset Resolution",
                self.get_persistent_path() + "simulatedxr/quadview/inset/resolution",
                1024,
                8192,
                100,
                labels=[("W", 0xFF353585), ("H", 0xFF853331)],
                tooltip="Resolution to simulate for inset targetted at the fovea",
            )

            omni.ui.Spacer(height=15)

            self.add_setting(
                SettingType.DOUBLE2,
                "Background Horizontal FOV Range",
                self.get_persistent_path() + "simulatedxr/quadview/background/fovX",
                -3,
                3,
                0.1,
                labels=[("O", 0xFF353585), ("I", 0xFF853331)],
                tooltip="Inner and outer (from nose) horizontal field of view tangents for background image",
            )

            self.add_setting(
                SettingType.DOUBLE2,
                "Background Vertical FOV Range",
                self.get_persistent_path() + "simulatedxr/quadview/background/fovY",
                -3,
                3,
                0.1,
                labels=[("B", 0xFF353585), ("T", 0xFF853331)],
                tooltip="Top and bottom vertical field of view tangents for background image",
            )

            omni.ui.Spacer(height=15)

            self.add_setting(
                SettingType.DOUBLE2,
                "Inset Horizontal FOV Range",
                self.get_persistent_path() + "simulatedxr/quadview/inset/fovX",
                -3,
                3,
                0.1,
                labels=[("O", 0xFF353585), ("I", 0xFF853331)],
                tooltip="Inner and outer (from nose) horizontal field of view tangents for for foreground (fovea) image",
            )

            self.add_setting(
                SettingType.DOUBLE2,
                "Inset Vertical FOV Range",
                self.get_persistent_path() + "simulatedxr/quadview/inset/fovY",
                -3,
                3,
                0.1,
                labels=[("B", 0xFF353585), ("T", 0xFF853331)],
                tooltip="Top and bottom vertical field of view tangents for foreground (fovea) image",
            )
