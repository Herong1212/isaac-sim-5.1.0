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

from ..ui.settings_frame import XRSettingsFrame


class XRMenuSimulationFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Simulation Settings"

    def _ui_subsection_separation(self):
        omni.ui.Spacer(height=8)
        omni.ui.Line()
        omni.ui.Spacer(height=8)

    def build_ui(self):

        self.add_setting(
            SettingType.FLOAT,
            "Framerate Cap",
            self.get_persistent_path() + "simulatedxr/refreshRate",
            1,
            360,
            1,
            tooltip="Refresh rate for simulation",
        )

        self.add_setting(
            SettingType.BOOL,
            "Simulate Depth",
            self.get_persistent_path() + "simulatedxr/depth/enabled",
            tooltip="Simulate depth texture and submit in simulator",
        )

        self.add_setting(
            SettingType.FLOAT,
            "User Height (m)",
            self.get_persistent_path() + "simulatedxr/userHeight",
            0.0,
            2.5,
            0.1,
            tooltip="User height to simulate",
        )

        self.add_setting(
            SettingType.FLOAT,
            "User Distance (m)",
            self.get_persistent_path() + "simulatedxr/userDistance",
            0.0,
            5.0,
            0.1,
            tooltip="User distance from origin",
        )

        self.add_setting(
            SettingType.FLOAT,
            "User Angle (m)",
            self.get_persistent_path() + "simulatedxr/userAngle",
            0.0,
            360.0,
            1.0,
            tooltip="User angle relative to origin",
        )
