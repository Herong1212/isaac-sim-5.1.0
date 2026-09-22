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

import omni.ui
from omni.kit.widget.settings import SettingType

from .xr_menu_simulation_frame import XRMenuSimulationFrame


class XRMenuSimulationTabletFrame(XRMenuSimulationFrame):
    def get_frame_name(self):
        return "Simulation Settings"

    def build_ui(self):

        super().build_ui()

        self._ui_subsection_separation()

        self.add_setting(
            SettingType.INT2,
            "Resolution",
            self.get_persistent_path() + "simulatedxr/tablet/resolution",
            300,
            8192,
            100,
            labels=[("W", 0xFF353585), ("H", 0xFF853331)],
            tooltip="Simulated resolution for tablet",
        )

        omni.ui.Spacer(height=15)

        self.add_setting(
            SettingType.DOUBLE2,
            "Tablet Horizontal FOV Range",
            self.get_persistent_path() + "simulatedxr/tablet/fovX",
            -3,
            3,
            0.1,
            labels=[("L", 0xFF353585), ("R", 0xFF853331)],
            tooltip="Left and right field of view tangents for tablet view",
        )

        self.add_setting(
            SettingType.DOUBLE2,
            "Tablet Vertical FOV Range",
            self.get_persistent_path() + "simulatedxr/tablet/fovY",
            -3,
            3,
            0.1,
            labels=[("B", 0xFF353585), ("T", 0xFF853331)],
            tooltip="Top and bottom field of view tangents for tablet view",
        )
