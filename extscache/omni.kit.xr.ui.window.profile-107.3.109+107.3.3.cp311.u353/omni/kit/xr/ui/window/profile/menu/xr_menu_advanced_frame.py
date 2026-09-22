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

from ..ui.settings_frame import XRSettingsFrame
from ..ui.settings_stack import XRSettingsStack

# =======================================================
# Advanced Frame
#
# Contains:
# - AdvancedSettings
# =======================================================


class XRMenuAdvancedFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Advanced Settings"

    def build_ui(self):
        config = self.get_config()
        if "components" in config:
            self.__settings_frame = XRSettingsStack(config["components"])
            self.__settings_frame.build_ui(self.get_profile())

    def is_advanced(self):
        return True
