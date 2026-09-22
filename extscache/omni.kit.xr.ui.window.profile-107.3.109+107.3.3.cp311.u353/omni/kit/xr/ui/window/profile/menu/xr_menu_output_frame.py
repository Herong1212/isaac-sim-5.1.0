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

from omni.kit.widget.settings import SettingType

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing where the XR output needs
# to be directed to.
#
# Contains:
# - switch to disable output of XR
# =======================================================


class XRMenuOutputFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Output"

    def build_ui(self):

        self.add_setting(
            SettingType.BOOL,
            "Disable XR Output",
            self.get_persistent_path() + "disableDisplayOutput",
            tooltip="Disable XR output for the case one only wants to use the object tracking.",
        )
