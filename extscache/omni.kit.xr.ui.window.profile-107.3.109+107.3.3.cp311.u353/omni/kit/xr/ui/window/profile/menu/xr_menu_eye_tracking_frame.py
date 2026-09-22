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
# Menu component describing eye tracking settings for VR
#
# Contains:
# - Enable switch
# - Resolution settings for different foveation options
# =======================================================


class XRMenuEyeTrackingFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Eye Tracking Settings"

    def build_ui(self):

        self.add_setting(
            SettingType.BOOL, "Enable Eye Tracking if Available", self.get_persistent_path() + "enableEyeTracking"
        )

        self.add_setting(
            SettingType.FLOAT,
            "Percentage of Full Resolution",
            self.get_persistent_path() + "foveationWarpedResolutionMultiplier",
            0.1,
            1,
            0.01,
        )
        self.add_setting(
            SettingType.FLOAT,
            "Relative Size of Unwarped Area",
            self.get_persistent_path() + "foveationWarpedInsetSize",
            0.1,
            1,
            0.01,
        )
