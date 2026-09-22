# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["XrPreferencesPage", "INTERACT_FREEZE_DELAY_SETTING_KEY"]

import omni.ui as ui
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX, PreferenceBuilder, SettingType

INTERACT_FREEZE_DELAY_SETTING_KEY: str = PERSISTENT_SETTINGS_PREFIX + "/xr/ui/interactFreezeDelay"


class XrPreferencesPage(PreferenceBuilder):
    def __init__(self):
        super().__init__("XR")

    def build(self):
        with ui.VStack(height=0):
            with self.add_frame("XR Input"):
                with ui.VStack():
                    w = self.create_setting_widget(
                        "UI Interaction Freeze Duration",
                        INTERACT_FREEZE_DELAY_SETTING_KEY,
                        SettingType.FLOAT,
                        tooltip="Because VR interactions tend to be noisier than mouse movement, we\n"
                        "freeze movement input to the UI for a time after interacting in order\n"
                        "to help actions like double-clicking to be more reliable.",
                        range_from=0.0,
                        range_to=2.0,
                        height=20,
                    )
                    w.identifier = "ui_input_delay"
