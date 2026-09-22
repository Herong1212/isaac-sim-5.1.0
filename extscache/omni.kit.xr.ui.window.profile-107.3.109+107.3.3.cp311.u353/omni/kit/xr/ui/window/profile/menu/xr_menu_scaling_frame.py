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

import math

import carb.settings
import omni.ui
from omni.kit.widget.settings import SettingType
from omni.kit.xr.core import XRCore, XRWeakMethod

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing scaling of scene
# Often Usd files have incorrect values and this allows for
# an override of scaling to set the correct values
#
# Contains:
# - Current scale stage
# - Current scale XR User
# - Presets with different scale configurations
# - Slider/Selector for scale of the user
# =======================================================


class XRMenuScalingFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "User Scale Settings"

    def build_ui(self):

        # Scale is stored in different variables then shown on the screen
        carb.settings.get_settings().set_float("/defaults" + self.get_non_persistent_path() + "scale/value", 1.0)
        carb.settings.get_settings().set_string(
            "/defaults" + self.get_non_persistent_path() + "scale/string", "Scale 1:1"
        )

        with omni.ui.HStack():
            omni.ui.Label("Usd Stage Scale (meters/unit):", width=210, height=20)
            self._stage_label = omni.ui.Label("", height=20)

        with omni.ui.HStack():
            omni.ui.Label("XR User Scale (meters/unit):", width=210, height=20)
            self._xr_label = omni.ui.Label("", height=20)

        # There are two types of scale
        # - scale to look at the model where you are a given factor taller
        # - scale to adjust for incorrect usd settings

        # These are tuples on whether scale is relative and what the
        # scale factor is on units

        self._scale_definitions = {
            "Scale 1:1": (True, 1.0),
            "Scale 1:2": (True, 0.5),
            "Scale 1:5": (True, 0.2),
            "Scale 1:10": (True, 0.1),
            "Scale 1:20": (True, 0.05),
            "Scale 1:50": (True, 0.02),
            "Scale 1:100": (True, 0.01),
            "Scale 1:200": (True, 0.005),
            "Scale 1:500": (True, 0.002),
            "Scale 1:1000": (True, 0.001),
            "Scale 1:2000": (True, 0.0005),
            "Millimeters": (False, 0.001),
            "Centimeters": (False, 0.01),
            "Meters": (False, 1.0),
            "Inches": (False, 0.0254),
            "Feet": (False, 0.3048),
            "Yards": (False, 0.9144),
            "Other": "other",
        }

        # Update the ui components
        self._set_scale_string()
        self._set_scale()
        self._update_labels()

        scale_presets = []
        for scale_definition in self._scale_definitions.keys():
            scale_presets.append(scale_definition)

        # Preset of different scale scenarios
        self.add_setting_combo(
            "XR User Scale Preset",
            self.get_non_persistent_path() + "scale/string",
            scale_presets,
            XRWeakMethod(self._combo_callback),
            tooltip="Presets for scaling: select either a scale factor to make you x times bigger than the model\nor select a unit to override the default setting in usd.",
        )

        # Custom slider to change the size of the scale
        # the user experiences
        self.add_setting(
            SettingType.FLOAT,
            "XR User Scale Multiplier",
            self.get_non_persistent_path() + "scale/value",
            0.001,
            2,
            0.001,
            format="%.4f",
            callback=XRWeakMethod(self._number_callback),
            tooltip="Current relative scale factor of the user in XR relative to the scale of the usd stage.",
        )

    def _update_labels(self):

        stage_coordinate_system = XRCore.get_singleton().get_stage_coordinate_system()
        scale_factor = carb.settings.get_settings().get(self.get_persistent_path() + "scale/factor")
        scale_relative = carb.settings.get_settings().get(self.get_persistent_path() + "scale/relative")

        xr_scale = scale_factor
        if scale_relative:
            xr_scale = scale_factor * stage_coordinate_system.meters_per_unit

        self._stage_label.text = str(stage_coordinate_system.meters_per_unit)
        self._xr_label.text = str(xr_scale)

    def _set_scale_string(self):
        scale_factor = carb.settings.get_settings().get(self.get_persistent_path() + "scale/factor")
        scale_relative = carb.settings.get_settings().get(self.get_persistent_path() + "scale/relative")

        currentScaleString = carb.settings.get_settings().get(self.get_non_persistent_path() + "scale/string")

        for key, item in self._scale_definitions.items():
            if isinstance(item, tuple):
                if scale_relative == item[0] and math.isclose(item[1], scale_factor):
                    if currentScaleString != key:
                        carb.settings.get_settings().set(self.get_non_persistent_path() + "scale/string", key)
                    return

        if currentScaleString != "Other":
            carb.settings.get_settings().set(self.get_non_persistent_path() + "scale/string", "Other")

    def _set_scale(self):
        scale = carb.settings.get_settings().get(self.get_persistent_path() + "scale/factor")
        scale_relative = carb.settings.get_settings().get(self.get_persistent_path() + "scale/relative")

        if scale_relative is False:
            stage_coordinate_system = XRCore.get_singleton().get_stage_coordinate_system()
            scale = scale / stage_coordinate_system.meters_per_unit

        current_scale = carb.settings.get_settings().get(self.get_non_persistent_path() + "scale/value")
        if (
            not isinstance(scale, float)
            or not isinstance(current_scale, float)
            or not math.isclose(scale, current_scale)
        ):
            carb.settings.get_settings().set(self.get_non_persistent_path() + "scale/value", scale)

    def _combo_callback(self):

        scale_str = carb.settings.get_settings().get(self.get_non_persistent_path() + "scale/string")

        carb.log_warn(scale_str)

        if str(scale_str) == "Other":
            self._update_labels()
            return

        for key, item in self._scale_definitions.items():
            if key == scale_str:
                carb.settings.get_settings().set(self.get_persistent_path() + "scale/factor", item[1])
                carb.settings.get_settings().set(self.get_persistent_path() + "scale/relative", item[0])
                self._set_scale()
                self._update_labels()
                return

    def _number_callback(self):
        current_scale = carb.settings.get_settings().get(self.get_non_persistent_path() + "scale/value")
        carb.settings.get_settings().set(self.get_persistent_path() + "scale/factor", current_scale)
        carb.settings.get_settings().set(self.get_persistent_path() + "scale/relative", True)
        self._set_scale_string()
        self._update_labels()
