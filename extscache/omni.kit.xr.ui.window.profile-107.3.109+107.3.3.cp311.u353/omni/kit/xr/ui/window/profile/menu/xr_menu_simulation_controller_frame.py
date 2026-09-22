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

from typing import List, Optional

import carb
import omni.ui
from omni.kit.widget.settings import SettingType
from omni.kit.xr.core import XRCore, XRInputDevice, XRToken

from ..ui.settings_frame import XRSettingsFrame

XR_SIMULATED_LEFT_CONTROLLERS = "/xr/simulatedxr/leftControllerTypes"
XR_SIMULATED_RIGHT_CONTROLLERS = "/xr/simulatedxr/rightControllerTypes"


class XRMenuSimulationControllerFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Simulation Controllers"

    def _ui_subsection_separation(self):
        omni.ui.Spacer(height=8)
        omni.ui.Line()
        omni.ui.Spacer(height=8)

    def build_ui(self):

        left_controller_types = carb.settings.get_settings().get(XR_SIMULATED_LEFT_CONTROLLERS)
        right_controller_types = carb.settings.get_settings().get(XR_SIMULATED_RIGHT_CONTROLLERS)

        self.add_setting_combo(
            "Left Controller Type",
            self.get_persistent_path() + "simulatedxr/controllers/leftType",
            left_controller_types,
            tooltip="What type controller to simulate for left hand",
        )

        self.add_setting_combo(
            "Right Controller Type",
            self.get_persistent_path() + "simulatedxr/controllers/rightType",
            right_controller_types,
            tooltip="What type controller to simulate for right hand",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Controller Distance (m)",
            self.get_persistent_path() + "simulatedxr/controllers/distance",
            0.1,
            1.0,
            0.01,
            tooltip="Distance along forward axis",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Controller Separation (m)",
            self.get_persistent_path() + "simulatedxr/controllers/separation",
            0.1,
            1.0,
            0.01,
            tooltip="Distance between controllers",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Controller Height (m)",
            self.get_persistent_path() + "simulatedxr/controllers/height",
            -0.7,
            0.7,
            0.01,
            tooltip="Height of the controllers (m)",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Angle around x-axis",
            self.get_persistent_path() + "simulatedxr/controllers/xAngle",
            0,
            90,
            1,
            tooltip="Angle around left-right axis",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Angle around y-axis",
            self.get_persistent_path() + "simulatedxr/controllers/yAngle",
            0,
            90,
            1,
            tooltip="Angle around vertical axis",
        )

        self.add_rebuild_subscription(XR_SIMULATED_LEFT_CONTROLLERS)
        self.add_rebuild_subscription(XR_SIMULATED_RIGHT_CONTROLLERS)

        self.add_rebuild_on_messagebus("xr_input.user_hand_left.inputs_change")
        self.add_rebuild_on_messagebus("xr_input.user_hand_right.inputs_change")

        self.layout_buttons("Left Controller", "/user/hand/left")
        self.layout_buttons("Right Controller", "/user/hand/right")

    def make_button(self, input_device, input):

        def press_fn():
            input_device.set_input_gesture_value(input, "click", 1.0)

        def release_fn():
            input_device.set_input_gesture_value(input, "click", 0.0)

        with omni.ui.HStack():
            omni.ui.Label(str(input))
            omni.ui.Spacer()
            omni.ui.Button(
                "PRESS",
                mouse_pressed_fn=lambda *_: press_fn(),
                mouse_released_fn=lambda *_: release_fn(),
                width=160,
                height=28,
                style={"border_radius": 4},
                tooltip="Click here to press button.",
            )
            omni.ui.Spacer(width=35)

    def layout_buttons(self, label_name: str, device_name: str):

        input_device: Optional[XRInputDevice] = XRCore.get_singleton().get_input_device(device_name)

        if input_device is None:
            return

        self._ui_subsection_separation()
        omni.ui.Label(label_name)

        inputs: List[XRToken] = input_device.get_input_names()
        input_names = []
        for input in inputs:
            input_names.append(str(input))
        input_names.sort()
        for input in input_names:
            gestures: List[XRToken] = input_device.get_input_gesture_names(input)

            if XRToken("click") in gestures:
                self.make_button(input_device, input)
