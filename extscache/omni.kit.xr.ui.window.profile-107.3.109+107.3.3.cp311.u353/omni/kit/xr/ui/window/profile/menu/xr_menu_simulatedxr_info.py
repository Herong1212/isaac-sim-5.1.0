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

import omni.ui as ui

from ..ui.settings_frame import XRSettingsFrame


class XRMenuSimulatedXRInfo(XRSettingsFrame):
    def get_frame_name(self):

        return "Information"

    def build_ui(self):

        with ui.VStack():

            ui.Label("What is SimulatedXR?", style={"font_size": 16.0, "color": 0xFFFFFFFF})
            ui.Spacer(height=5)
            ui.Label(
                "SimulatedXR is for testing purposes only, it simulates an XR device but does not require an actual xr device to be attached. "
                + "It can be configured to pace and a given rate with a given of set of displays.",
                word_wrap=True,
            )
            ui.Spacer(height=10)
