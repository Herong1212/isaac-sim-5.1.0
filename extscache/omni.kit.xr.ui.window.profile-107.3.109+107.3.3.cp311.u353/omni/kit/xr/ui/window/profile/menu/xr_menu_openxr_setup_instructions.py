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
import omni.ui as ui

from ..ui.settings_frame import XRSettingsFrame


class XRMenuOpenXRSetupInstructions(XRSettingsFrame):
    def get_frame_name(self):

        return "Setup Instructions"

    def build_ui(self):

        with ui.VStack():

            ui.Label("How to setup OpenXR?", style={"font_size": 16.0, "color": 0xFFFFFFFF})
            ui.Spacer(height=5)
            ui.Label(
                "When an OpenXR runtime for an XR device is installed on a system it will be registered in the operating system. "
                + "This extension will locate the runtime and by pressing start at the top of the menu it will connect and activate the runtime.",
                word_wrap=True,
            )
            ui.Spacer(height=10)

            ui.Label("How to obtain OpenXR runtime?", style={"font_size": 16.0, "color": 0xFFFFFFFF})
            ui.Spacer(height=5)
            ui.Label(
                "Each device vendor will have its own instructions for installing an OpenXR runtime on the system.",
                word_wrap=True,
            )
            ui.Spacer(height=10)
