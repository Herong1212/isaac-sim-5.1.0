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
# Menu component describing clipping planes used in XR
# TODO: Should hide these settings as they should not really be changed
#
# Contains:
# - far and near definitions
#
# =======================================================


class XRMenuClippingPlanesFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Clipping Planes"

    def build_ui(self):
        self.add_setting(
            SettingType.FLOAT,
            "Near Plane (in meters)",
            self.get_persistent_path() + "render/nearPlane",
            0.001,
            0.1,
            0.001,
            tooltip="Near clipping plane for XR rendering in meters",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Far Plane (in meters)",
            self.get_persistent_path() + "render/farPlane",
            10,
            10000,
            10,
            tooltip="Far clipping plane for XR rendering in meters",
        )
