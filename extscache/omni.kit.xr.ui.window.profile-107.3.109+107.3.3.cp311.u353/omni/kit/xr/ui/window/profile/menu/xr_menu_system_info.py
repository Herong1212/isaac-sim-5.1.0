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

from ..ui.settings_frame import XRSettingsFrame
from ..ui.settings_stack import XRSettingsStack
from .xr_menu_openxr_info import XRMenuOpenXRInfo
from .xr_menu_openxr_setup_instructions import XRMenuOpenXRSetupInstructions
from .xr_menu_simulatedxr_info import XRMenuSimulatedXRInfo
from .xr_menu_simulation_controller_frame import XRMenuSimulationControllerFrame
from .xr_menu_simulation_stereo_frame import XRMenuSimulationStereoFrame
from .xr_menu_simulation_tablet_frame import XRMenuSimulationTabletFrame
from .xr_menu_xcr_frame import XRMenuXCRFrame

OPENXR_SYSTEM = "OpenXR"
SIMULATEDXR_SYSTEM = "SimulatedXR"


class XRMenuSystemInfo(XRSettingsFrame):
    def _get_current_system(self) -> str:
        return carb.settings.get_settings().get(self.get_persistent_path() + "system/display")

    def get_frame_name(self):
        current_system = self._get_current_system()
        if not isinstance(current_system, str):
            current_system = ""

        ui_header_suffix = "Information/Setup for"
        if current_system == SIMULATEDXR_SYSTEM:
            ui_header_suffix = "Information/Settings for"

        return f"{ui_header_suffix} {current_system}"

    def build_ui(self):
        self.add_rebuild_subscription(self.get_persistent_path() + "system/display")
        current_system = self._get_current_system()

        components = []
        if current_system == OPENXR_SYSTEM:
            components = [XRMenuOpenXRSetupInstructions, XRMenuOpenXRInfo, XRMenuXCRFrame]
        elif current_system == SIMULATEDXR_SYSTEM:
            components = [XRMenuSimulatedXRInfo]
            systemDisplayMode = carb.settings.get_settings().get(self.get_non_persistent_path() + "system/displayMode")
            if systemDisplayMode == "TabletAR":
                components.append(XRMenuSimulationTabletFrame)
            else:
                components.append(XRMenuSimulationStereoFrame)
                components.append(XRMenuSimulationControllerFrame)

        self.__settings_frame = XRSettingsStack(components)
        self.__settings_frame.build_ui(self.get_profile())

    def is_info(self):
        return True
